"""Execução e recálculo do LumiBench."""

import json
import math
import os
import platform
import re
import subprocess
import sys
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

from adapters import backends, outputs

from . import data, prompts, report
from .files import new_directory, write_json, write_jsonl

ROOT = data.ROOT
DEFAULT_CONFIG = ROOT / "configs/benchmark.dummy.json"
CONTRACT = "lumi-lab-lumibench-v1"


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), *args], text=True, stderr=subprocess.DEVNULL, timeout=5,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def code_info():
    status = git("status", "--porcelain")
    files = [*sorted((ROOT / "benchmark").glob("*.py")), *sorted((ROOT / "adapters").rglob("*.py")),
             *sorted((ROOT / "adapters/native").glob("*.cpp"))]
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status),
            "files_sha256": {str(path.relative_to(ROOT)): data.digest(path.read_bytes()) for path in files}}


def scoring_revision():
    files = ("benchmark/extract.py", "benchmark/toolcall.py", "benchmark/metrics.py",
             "benchmark/report.py", "adapters/outputs.py")
    return data.digest(b"\0".join((ROOT / name).read_bytes() for name in files))


def configuration(path):
    raw = path.read_bytes()
    config = json.loads(raw)
    if not isinstance(config, dict) or set(config) - {"backend", "model", "adapter", "prompt_variant", "generation"}:
        raise ValueError("Configuração de execução inválida")
    backend = config.get("backend")
    if not isinstance(backend, dict):
        raise ValueError("Configure backend como objeto")
    kind = backend.get("type")
    allowed = {
        "dummy": set(),
        "openai_compat": {"base_url", "model", "api_key_env", "timeout"},
        "choice_logits": {"executable", "weights", "template", "context_size"},
    }
    if kind not in allowed or set(backend) - {"type"} - allowed[kind]:
        raise ValueError("Backend ou opções desconhecidas")
    model = config.get("model", {})
    if kind != "dummy":
        if not isinstance(model, dict):
            raise ValueError("Configure model como objeto")
        for field in ("revision", "tokenizer_revision"):
            if not re.fullmatch(r"(?:[a-f0-9]{40}|[a-f0-9]{64})", str(model.get(field, ""))):
                raise ValueError(f"Fixe model.{field} com commit ou SHA-256")
        for field in ("quantization", "runtime", "hardware"):
            value = model.get(field)
            if not isinstance(value, str) or not value.strip() or "PREENCHER" in value:
                raise ValueError(f"Informe model.{field}")
    if kind == "openai_compat":
        url = urlsplit(backend.get("base_url", ""))
        if url.scheme not in ("http", "https") or not url.hostname or "@" in url.netloc or url.query or url.fragment:
            raise ValueError("Informe uma URL de servidor sem credenciais, query ou fragmento")
        if not backend.get("model"):
            raise ValueError("Informe o identificador do modelo servido")
        timeout = backend.get("timeout", 300)
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout do servidor deve ser positivo")
    if kind == "choice_logits":
        if not re.fullmatch(r"[a-f0-9]{64}", str(model.get("chat_template_sha256", ""))):
            raise ValueError("Fixe model.chat_template_sha256 com o SHA-256 do template")
        if not all(isinstance(backend.get(key), str) and backend[key]
                   for key in ("executable", "weights", "template")):
            raise ValueError("Informe executable, weights e template para choice_logits")
        context_size = backend.get("context_size")
        if type(context_size) is not int or not 4 <= context_size <= 32768:
            raise ValueError("Contexto de choice_logits deve estar entre 4 e 32768")
        if config.get("prompt_variant", "direct") != "direct":
            raise ValueError("choice_logits usa o prompt direct")
    if config.get("adapter", "default") not in outputs.ADAPTERS:
        raise ValueError("Adaptador desconhecido")
    if config.get("prompt_variant", "direct") not in {"direct", "cot"}:
        raise ValueError("Variante de prompt esperada: direct ou cot")
    generation = {"max_new_tokens": 512, "temperature": 0.0, "seed": 42}
    generation.update(config.get("generation", {}))
    if (set(generation) != {"max_new_tokens", "temperature", "seed"}
            or type(generation["max_new_tokens"]) is not int or generation["max_new_tokens"] < 1
            or type(generation["seed"]) is not int
            or type(generation["temperature"]) not in (int, float)
            or not math.isfinite(generation["temperature"]) or generation["temperature"] < 0):
        raise ValueError("Parâmetros de geração inválidos")
    return config, raw, generation


def load_suite(suite, directory):
    if suite == "lumibench":
        return data.load_snapshot(directory)
    if suite == "demo":
        return data.load_demo()
    raise ValueError(f"Suite desconhecida: {suite}")


def select(bundle, split, datasets=(), limit=None):
    requested = set(datasets) if datasets else set(bundle)
    if not requested <= set(bundle):
        raise ValueError(f"Datasets desconhecidos: {sorted(requested - set(bundle))}")
    selected, sources = {}, {}
    for name, (path, track, content, rows) in bundle.items():
        if name not in requested:
            continue
        examples = [row for row in rows if row["split"] == split][:limit]
        if not examples:
            raise ValueError(f"{name}: nenhum exemplo no split {split}")
        selected.setdefault(track, []).extend(examples)
        sources[name] = {"file": path.name, "sha256": data.digest(content)}
    return selected, sources


def predict(backend, track, example, variant, adapter, generation):
    if track == "conhecimento":
        messages = prompts.mcq_messages(example, variant)
        letters = "".join(sorted(example["choices"]))
    else:
        messages, letters = prompts.decision_messages(example), None
    try:
        response = backend.generate(messages, choice_letters=letters, **generation)
        raw, calls = response["text"], response.get("tool_calls")
        if not isinstance(raw, str) or (calls is not None and not isinstance(calls, list)):
            raise ValueError("Resposta do backend fora do contrato")
        row = {"id": example["id"], "raw_output": raw, "tool_calls": calls,
               "normalized_output": outputs.adapt(adapter, track, raw, calls),
               "reasoning_output": response.get("reasoning_output"), "finish_reason": response.get("finish_reason"),
               "latency_s": response.get("latency_s"), "n_gen_tokens": response.get("n_gen_tokens"),
               "error": None}
        for key in ("choice_logits", "choice_token_ids", "prompt_tokens"):
            if key in response:
                row[key] = response[key]
        json.dumps(row, allow_nan=False)
        return row
    except (TimeoutError, URLError) as exc:
        error = f"HTTPError:{exc.code}" if isinstance(exc, HTTPError) else type(exc).__name__
    except Exception as exc:
        error = type(exc).__name__
    return {"id": example["id"], "raw_output": "", "normalized_output": "", "error": error}


def execute(config_path, output, *, suite="lumibench", directory=data.DEFAULT_DATA,
            split="dev", datasets=(), limit=None):
    if split not in {"dev", "test"} or (limit is not None and limit < 1):
        raise ValueError("Use split dev/test e limite positivo")
    if split == "test" and limit is not None:
        raise ValueError("O teste usa todos os itens de cada dataset selecionado")
    config, raw_config, generation = configuration(config_path)
    bundle = load_suite(suite, directory)
    selected, sources = select(bundle, split, datasets, limit)
    native_choices = config["backend"]["type"] == "choice_logits"
    if native_choices and "decisao" in selected:
        raise ValueError("choice_logits requer selecionar somente bases de múltipla escolha")
    with new_directory(output) as stage, ExitStack() as resources:
        if native_choices:
            from adapters.choice_logits import ChoiceLogitsBackend
            backend = ChoiceLogitsBackend(config["backend"], config["model"])
            resources.callback(backend.close)
        else:
            backend = backends.make_backend(config["backend"])
        adapter, variant = config.get("adapter", "default"), config.get("prompt_variant", "direct")
        manifest = {
            "contract": CONTRACT, "run_id": output.name, "started_at": now(),
            "suite": suite, "split": split, "partial": bool(limit or set(sources) != set(bundle)),
            "datasets": sources, "limit_per_dataset": limit,
            "snapshot": json.loads(data.LOCK.read_bytes())["commit"] if suite == "lumibench" else None,
            "sample_ids": {track: data.ids_for(rows) for track, rows in selected.items()},
            "code": code_info(), "scoring_revision": scoring_revision(),
            "config_sha256": data.digest(raw_config), "backend": backend.info(),
            "model": config.get("model"), "adapter": adapter,
            "prompt_version": prompts.PROMPT_VERSION, "prompt_variant": variant, "generation": generation,
            "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                            "cpu_count": os.cpu_count()},
            "measurement": {"latency_s": "segundos medidos pelo backend",
                            "n_gen_tokens": "tokens de saída reportados pelo backend, quando disponíveis"},
        }
        predictions = {}
        for track, rows in selected.items():
            predictions[track] = [predict(backend, track, row, variant, adapter, generation) for row in rows]
            write_jsonl(stage / f"predicoes_{track}.jsonl", predictions[track])
        manifest["finished_at"] = now()
        manifest["prediction_hashes"] = {
            track: data.digest((stage / f"predicoes_{track}.jsonl").read_bytes()) for track in predictions
        }
        (stage / "config.json").write_bytes(raw_config)
        write_json(stage / "manifest.json", manifest)
        report.build(stage, selected, predictions, manifest)
    return output


def replay(run_dir, output, *, directory=data.DEFAULT_DATA):
    original = (run_dir / "manifest.json").read_bytes()
    manifest = json.loads(original)
    if manifest["contract"] != CONTRACT or manifest["scoring_revision"] != scoring_revision():
        raise ValueError("Use a mesma revisão de pontuação da execução original")
    bundle = load_suite(manifest["suite"], directory)
    selected, sources = select(bundle, manifest["split"], manifest["datasets"], manifest["limit_per_dataset"])
    if sources != manifest["datasets"] or {
        track: data.ids_for(rows) for track, rows in selected.items()
    } != manifest["sample_ids"]:
        raise ValueError("Dados, hashes ou IDs diferentes da execução original")
    predictions, prediction_hashes = {}, {}
    for track in selected:
        path = run_dir / f"predicoes_{track}.jsonl"
        if path.exists():
            content = path.read_bytes()
            predictions[track] = data.parse_jsonl(content, str(path))
            prediction_hashes[track] = data.digest(content)
        else:
            predictions[track], prediction_hashes[track] = [], None
    with new_directory(output) as stage:
        report.build(stage, selected, predictions, manifest)
        write_json(stage / "replay.json", {
            "original_run_id": manifest["run_id"], "original_manifest_sha256": data.digest(original),
            "prediction_hashes": prediction_hashes,
            "changed_predictions": sorted(track for track, digest in prediction_hashes.items()
                                          if digest != manifest["prediction_hashes"][track]),
            "scoring_revision": scoring_revision(),
        })
    return output
