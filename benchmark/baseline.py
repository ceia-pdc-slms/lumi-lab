"""Reprodução do baseline LumiBench direct com o avaliador upstream."""
import argparse
from collections import Counter
from importlib import import_module
import json
from pathlib import Path
import shutil
from statistics import median, quantiles
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from unittest.mock import patch
from urllib.request import Request, urlopen

from . import data
from .files import new_directory, write_json

SOURCE = data.ROOT / ".cache/lumi-benchmark"
PROTOCOL = json.loads((data.CATALOG / "protocol.json").read_bytes())
PROFILE = data.CATALOG / "profiles/ollama-direct"
RUNTIME = json.loads((PROFILE / "runtime.json").read_bytes())
COMMIT = PROTOCOL["evaluator"]["commit"]
REPOSITORY = PROTOCOL["evaluator"]["repository"]
URL = RUNTIME["base_url"]
CONTEXT = RUNTIME["context_tokens"]
REASONING = RUNTIME["reasoning_effort"]
GENERATION = RUNTIME["generation"]
FILES = PROTOCOL["files"]


def fetch_json(endpoint, body=None, timeout=15):
    payload = None if body is None else json.dumps(body).encode()
    request = Request(URL + endpoint, payload, {"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def read_predictions(path, ids):
    rows = data.parse_jsonl(path.read_bytes(), str(path))
    if [row["id"] for row in rows] != ids:
        raise ValueError(f"IDs ausentes, repetidos ou fora da ordem: {path}")
    return rows


def source_ready(source):
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True)
    status = subprocess.check_output(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all", "--", "lumi_bench"],
        text=True,
    )
    if head.strip() != COMMIT or status:
        raise ValueError(f"Use o checkout limpo de {COMMIT} em {source}")


def prepare(source, directory):
    if not source.exists():
        with new_directory(source) as stage:
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", REPOSITORY, str(stage)], check=True)
            subprocess.run(["git", "-C", str(stage), "checkout", "--quiet", "--detach", COMMIT], check=True)
    source_ready(source)
    data.install_snapshot(source, directory)
    print(f"Dados validados em {directory} (313 dev, 687 test)")


def upstream(source, module):
    source_ready(source)
    sys.path.insert(0, str(source.resolve()))
    sys.dont_write_bytecode = True
    return import_module(f"lumi_bench.{module}")


class OllamaTransport:
    def __init__(self, model):
        self.model = model
        alias = model["alias"]
        entry = next((x for x in fetch_json("/api/tags")["models"] if x["name"] == alias), None)
        if entry is None or entry["digest"] != model["ollama_model_digest"]:
            raise ValueError(f"Alias ou digest incorreto para {alias}. Consulte benchmarks/lumibench/v1/.")
        template = fetch_json("/api/show", {"model": alias})["template"]
        if data.digest(template.encode()) != model["chat_template_sha256"]:
            raise ValueError(f"Chat template divergente: {alias}")
        self.version = fetch_json("/api/version")["version"]

    def generate(self, messages, max_new_tokens=512, temperature=0, seed=42, choice_letters=None):
        started = perf_counter()
        response = fetch_json("/v1/chat/completions", {
            "model": self.model["alias"], "messages": messages, "max_tokens": max_new_tokens,
            "temperature": temperature, "seed": seed, "reasoning_effort": REASONING,
        }, timeout=600)
        latency = perf_counter() - started
        message = response["choices"][0]["message"]
        if any(message.get(key) for key in ("reasoning_content", "reasoning", "thinking", "tool_calls")):
            raise ValueError("O endpoint devolveu raciocínio ou chamada nativa fora do contrato")
        return {"text": message.get("content") or "", "latency_s": latency,
                "n_gen_tokens": (response.get("usage") or {}).get("completion_tokens")}

    def warmup(self):
        self.generate([{"role": "user", "content": "Responda somente com a palavra pronto."}], max_new_tokens=32)
        active = next((x for x in fetch_json("/api/ps")["models"] if x["name"] == self.model["alias"]), None)
        if not active or active["context_length"] != CONTEXT:
            raise ValueError(f"Contexto ativo diferente de {CONTEXT} tokens")
        self.loaded = {key: active.get(key) for key in ("context_length", "size", "size_vram")}

    def info(self):
        return {
            "backend": "openai_compat", "base_url": URL + "/v1", "model": self.model["alias"],
            "runtime": self.version, "context": CONTEXT, "reasoning_effort": REASONING,
            **self.loaded,
            **{key: self.model[key] for key in ("artifact", "weights_sha256",
                                                "ollama_model_digest", "chat_template_sha256")},
        }


def configure(split, model, limit):
    paths = {track: [f"data/benchmark/{name}.jsonl" for name in datasets]
             for track, datasets in FILES.items()}
    config = {
        "run_name": "evaluation", "backend": {"type": "openai_compat", "base_url": URL + "/v1",
                                              "model": model["alias"], "want_probs": False, "timeout": 600},
        "split": split, "prompt_variant": PROTOCOL["prompt_variant"], "adapter": PROTOCOL["adapter"], **GENERATION,
        "quantization": model["quantization"], "output_dir": "runs", "data": paths,
    }
    if limit is not None:
        if split != "dev" or limit < 1:
            raise ValueError("--limit aceita um inteiro positivo em dev")
        config["limit"] = limit
    return config


def execute(source, directory, out, model_name, split, limit):
    runner = upstream(source, "run")
    bundle = data.load_snapshot(directory)
    model = json.loads((PROFILE / "models.json").read_bytes())[model_name]
    config = configure(split, model, limit)
    with new_directory(out) as stage, TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "configs").mkdir()
        (root / "data/benchmark").mkdir(parents=True)
        for path, _, content, _ in bundle.values():
            (root / "data/benchmark" / path.name).write_bytes(content)
        config_path = root / "configs/run.json"
        write_json(config_path, config)
        backend = OllamaTransport(model)
        backend.warmup()
        # O upstream executa o fluxo inteiro, com o transporte Ollama injetado.
        with patch.object(runner.backends, "make_backend", return_value=backend), \
                patch.object(runner, "git_commit", return_value=COMMIT):
            runner.main(["--config", str(config_path)])
        for artifact in (root / "runs" / config["run_name"]).iterdir():
            shutil.move(artifact, stage / artifact.name)
        shutil.copy2(config_path, stage / "config.json")
    print(out)


def score_run(report, folder, bundle, split):
    manifest = json.loads((folder / "manifest.json").read_bytes())
    if (manifest["git_commit"], manifest["split"], manifest["prompt_version"],
            manifest["prompt_variant"], manifest["adapter"], manifest["generation"]) != (
            COMMIT, split, PROTOCOL["prompt_version"], PROTOCOL["prompt_variant"], PROTOCOL["adapter"], GENERATION
    ):
        raise ValueError(f"Protocolo diferente: {folder}")
    scored = {}
    for track, scorer in (("conhecimento", report.score_knowledge), ("decisao", report.score_decision)):
        expected = {f"data/benchmark/{path.name}": (content, rows) for path, kind, content, rows in bundle.values()
                    if kind == track}
        specs = manifest["data"][track]
        if [spec["path"] for spec in specs] != [f"data/benchmark/{name}.jsonl" for name in FILES[track]]:
            raise ValueError(f"Arquivos de dados divergentes: {folder} / {track}")
        examples = []
        for spec in specs:
            content, rows = expected[spec["path"]]
            if spec["sha256"] not in {data.digest(content), data.digest(content.replace(b"\n", b"\r\n"))}:
                raise ValueError(f"Hash de dados divergente: {folder} / {spec['path']}")
            examples.extend(row for row in rows if row["split"] == split)
        if manifest["n_examples"][track] != len(examples):
            raise ValueError(f"Cobertura divergente: {folder} / {track}")
        predictions = read_predictions(folder / f"predicoes_{track}.jsonl", data.ids_for(examples))
        failures = sum(bool(row.get("error")) for row in predictions)
        scored[track] = (scorer(examples, predictions), failures)
    return manifest, scored


def latency(rows):
    values = [row["latency_s"] for row in rows if row["latency_s"] is not None]
    return {"n_medicoes": len(values), "mediana_s": median(values) if values else None,
            "p95_s": quantiles(values, n=100, method="inclusive")[94] if len(values) > 1 else next(iter(values), None)}


def compare(source, directory, split, lumi, qwen):
    report = upstream(source, "report")
    bundle = data.load_snapshot(directory)
    runs = {"lumi": score_run(report, lumi, bundle, split), "qwen3": score_run(report, qwen, bundle, split)}
    result = {"split": split, "commit_avaliador": COMMIT, "modelos": {}, "trilhas": {}}
    profiles = json.loads((PROFILE / "models.json").read_bytes())
    for name, (manifest, _) in runs.items():
        backend = manifest["backend"]
        profile = profiles[name]
        required = {"model": profile["alias"], "context": CONTEXT, "reasoning_effort": REASONING}
        for key in ("weights_sha256", "ollama_model_digest", "chat_template_sha256"):
            required[key] = profile[key]
        if any(backend.get(key) != value for key, value in required.items()):
            raise ValueError(f"Identidade ou condições de inferência divergentes: {name}")
        result["modelos"][name] = {
            "backend": manifest["backend"], "quantizacao": manifest["quantization"],
            "duracao_s": manifest["finished_at"] - manifest["started_at"],
        }
    for track, flag in (("conhecimento", "correct"), ("decisao", "exact")):
        grouped = {}
        metrics = {"por_base": grouped, "modelos": {}}
        left, right = [scored[track][0] for _, scored in runs.values()]
        if [x["id"] for x in left] != [x["id"] for x in right]:
            raise ValueError(f"IDs das rodadas não coincidem: {track}")
        counts = Counter(row["dataset"] for row in left)
        for base, n in sorted(counts.items()):
            grouped[base] = {"n": n}
        for name, (_, scored) in runs.items():
            rows, failures = scored[track]
            correct = Counter(row["dataset"] for row in rows if row[flag])
            for base, entry in grouped.items():
                entry[name] = correct[base]
            metrics["modelos"][name] = {
                "n": len(rows), "acertos": sum(correct.values()), "falhas": failures, **latency(rows),
            }
        result["trilhas"][track] = metrics
    return result


def main(argv=None):
    """Mantém a invocação publicada antes do catálogo durante a transição."""
    from .__main__ import main as public_main

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--source")
    parser.add_argument("--data-dir")
    options, remaining = parser.parse_known_args(argv)
    for name, value in (("--source", options.source), ("--data-dir", options.data_dir)):
        if value is not None:
            remaining.extend([name, value])
    # A interface anterior exige o modelo; evita cair no avaliador integrado.
    if remaining and remaining[0] == "run" and not any(
        item == "--model" or item.startswith("--model=") for item in remaining
    ) and not {"--help", "-h"}.intersection(remaining):
        parser.error("run exige --model")
    return public_main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
