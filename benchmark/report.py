"""Pontua predições com o denominador do manifesto."""

import math

from adapters.outputs import adapt

from . import extract, metrics, toolcall
from .data import TRACKS, ids_for
from .files import write_json, write_jsonl


def score_rows(track, examples, predictions, adapter):
    expected = set(ids_for(examples))
    if set(ids_for(predictions)) - expected:
        raise ValueError(f"{track}: predições para IDs fora do manifesto")
    by_id = {row["id"]: row for row in predictions}
    rows = []
    for example in examples:
        pred = by_id.get(example["id"], {})
        error = pred.get("error") if pred else "missing_prediction"
        text = "" if error else adapt(adapter, track, pred["raw_output"], pred.get("tool_calls"))
        if track == "conhecimento":
            letter, rule = extract.extract_choice(text, "".join(sorted(example["choices"])))
            score = {"pred": letter, "gold": example["answer"], "extract_rule": rule,
                     "valid": letter is not None, "correct": letter == example["answer"]}
        else:
            score = toolcall.evaluate_decision(text, example)
        score.update({key: example[key] for key in ("id", "dataset", "sector", "task")})
        score.update(error=error, latency_s=pred.get("latency_s"), n_gen_tokens=pred.get("n_gen_tokens"))
        rows.append(score)
    return rows


def summarize(track, rows):
    summary = metrics.mcq_summary(rows) if track == "conhecimento" else metrics.decision_summary(rows)
    missing = sum(row["error"] == "missing_prediction" for row in rows)
    failures = sum(row["error"] is not None for row in rows) - missing
    return {**summary, "coverage": (len(rows) - missing) / len(rows),
            "missing_predictions": missing, "inference_failures": failures}


def json_metrics(value):
    if isinstance(value, dict):
        return {key: json_metrics(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_metrics(item) for item in value]
    return None if isinstance(value, float) and not math.isfinite(value) else value


def build(output, selected, predictions, manifest):
    result = {}
    report = [
        "# Avaliação LumiBench", "",
        f"- Suite `{manifest['suite']}` · split `{manifest['split']}`",
        f"- Prompt `{manifest['prompt_version']}` · `{manifest['prompt_variant']}`",
        f"- Backend `{manifest['backend']['backend']}`",
        f"- Recorte parcial: {'sim' if manifest['partial'] else 'não'}",
    ]
    if manifest["backend"]["backend"] == "dummy":
        report.append("- Execução de verificação com respostas fixas.")
    for track in TRACKS:
        if track not in selected:
            continue
        rows = score_rows(track, selected[track], predictions[track], manifest["adapter"])
        groups = {
            key: {name: summarize(track, subset)
                  for name, subset in sorted(metrics.group_by(rows, key).items())}
            for key in ("dataset", "sector", "task")
        }
        result[track] = {
            "geral": summarize(track, rows), **groups,
            "eficiencia": metrics.efficiency(rows),
        }
        primary = "accuracy" if track == "conhecimento" else "call_exact_match"
        label = "Trilha A · Conhecimento" if track == "conhecimento" else "Trilha B · Decisão"
        report.extend(["", f"## {label}", "", "| Grupo | N | Acerto | Cobertura | Falhas |",
                       "|---|---:|---:|---:|---:|"])
        for label, summary in [("Geral", result[track]["geral"]), *groups["dataset"].items()]:
            report.append(f"| {label} | {summary['n']} | {summary[primary]:.2%} | "
                          f"{summary['coverage']:.2%} | {summary['inference_failures']} |")
        write_jsonl(output / f"pontuacao_{track}.jsonl", rows)
    (output / "relatorio.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_json(output / "metricas.json", json_metrics(result))
