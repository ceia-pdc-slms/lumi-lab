"""Verifica três formatos de decisão no split dev do BFCL."""

import argparse
import json
from pathlib import Path

from adapters.backends import OpenAICompatBackend

from . import data, prompts, report, run
from .files import new_directory, write_json, write_jsonl

CASES = (("tool_selection", 1), ("irrelevance", 0), ("parallel_calls", 2))


def select_cases(rows):
    ordered = sorted(rows, key=lambda row: row["id"])
    selected = []
    for task, n_calls in CASES:
        example = next((row for row in ordered if row["split"] == "dev"
                        and row["task"] == task and len(row["gold_calls"]) == n_calls), None)
        if example is None:
            raise ValueError(f"BFCL dev sem caso {task} com {n_calls} chamada(s)")
        selected.append(example)
    return selected


def check(config_path, output, directory=data.DEFAULT_DATA):
    config, raw_config, generation = run.configuration(config_path)
    if config["backend"]["type"] != "openai_compat":
        raise ValueError("A verificação do contrato requer um servidor OpenAI-compatible")
    path, _, payload, rows = data.load_snapshot(directory)["bfcl_pt"]
    selected = select_cases(rows)
    track = "decisao"
    adapter = config.get("adapter", "default")
    variant = config.get("prompt_variant", "direct")
    backend = OpenAICompatBackend(**{key: value for key, value in config["backend"].items() if key != "type"})
    with new_directory(output) as stage:
        manifest = {
            "contract": run.CONTRACT, "run_id": output.name, "started_at": run.now(),
            "suite": "lumibench", "split": "dev", "partial": True,
            "selection": "Primeiro ID em ordem lexicográfica por tarefa e número de chamadas esperadas",
            "snapshot": json.loads(data.LOCK.read_bytes())["commit"],
            "datasets": {"bfcl_pt": {"file": path.name, "sha256": data.digest(payload)}},
            "sample_ids": {track: data.ids_for(selected)}, "scoring_revision": run.scoring_revision(),
            "code": run.code_info(), "config_sha256": data.digest(raw_config),
            "backend": backend.info(), "model": config["model"], "generation": generation,
            "adapter": adapter, "prompt_variant": variant, "prompt_version": prompts.PROMPT_VERSION,
        }
        requests = [{"id": row["id"], "body": backend.request_body(prompts.decision_messages(row), **generation)}
                    for row in selected]
        predictions = [run.predict(backend, track, row, variant, adapter, generation) for row in selected]
        write_jsonl(stage / "requisicoes.jsonl", requests)
        write_jsonl(stage / "gabaritos.jsonl", [
            {"id": row["id"], "task": row["task"], "gold_calls": row["gold_calls"]} for row in selected
        ])
        write_jsonl(stage / "predicoes_decisao.jsonl", predictions)
        (stage / "config.json").write_bytes(raw_config)
        manifest["finished_at"] = run.now()
        write_json(stage / "manifest.json", manifest)
        report.build(stage, {track: selected}, {track: predictions}, manifest)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, default=data.DEFAULT_DATA)
    parser.add_argument("--out", type=Path, required=True)
    opts = parser.parse_args()
    try:
        print(check(opts.config, opts.out, opts.data_dir))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
