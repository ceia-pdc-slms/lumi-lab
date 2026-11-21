"""Snapshot do LumiBench e auditoria local de candidatos de treino."""

import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from .files import new_directory
from .splits import find_duplicates, text_key

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ID = "lumibench/v1"
CATALOG = ROOT / "benchmarks" / BENCHMARK_ID
LOCK = CATALOG / "dataset.json"
DEFAULT_DATA = ROOT / "data/raw/lumibench-v1"
TRACKS = ("conhecimento", "decisao")


def digest(content):
    return hashlib.sha256(content).hexdigest()


def parse_jsonl(content, label):
    rows = []
    for n, line in enumerate(io.StringIO(content.decode("utf-8")), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"{label}:{n}: JSON inválido") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{label}:{n}: esperava objeto JSON")
        rows.append(row)
    return rows


def checked_bytes(content, spec):
    if digest(content) == spec["sha256_upstream_crlf"]:
        content = content.replace(b"\r\n", b"\n")
    if digest(content) != spec["sha256"]:
        raise ValueError(f"SHA-256 inesperado: {spec.get('file', 'JSONL')}")
    return content


def row_track(row):
    return "conhecimento" if "question" in row else "decisao"


def validate_row(row, track, allowed_splits):
    for field in ("id", "dataset", "source_id", "group_id", "sector", "task"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError(f"{row.get('id')}: campo obrigatório inválido: {field}")
    provenance = row.get("provenance")
    required = ("source", "source_version", "license", "language_origin")
    if not isinstance(provenance, dict) or any(
        not isinstance(provenance.get(key), str) or not provenance[key].strip() for key in required
    ):
        raise ValueError(f"{row['id']}: procedência incompleta")
    transformations = provenance.get("transformations")
    if not isinstance(transformations, list) or any(not isinstance(op, str) for op in transformations):
        raise ValueError(f"{row['id']}: transformações da procedência inválidas")
    if row.get("split") not in allowed_splits:
        raise ValueError(f"{row['id']}: split inválido")
    field = "question" if track == "conhecimento" else "query"
    if not isinstance(row.get(field), str) or not text_key(row):
        raise ValueError(f"{row['id']}: entrada vazia ou inválida")
    if track == "conhecimento":
        choices = row.get("choices")
        if ("question" not in row or row["task"] != "mcq" or not isinstance(choices, dict)
                or not 2 <= len(choices) <= 10 or not isinstance(row.get("answer"), str)
                or row["answer"] not in choices
                or any(k not in "ABCDEFGHIJ" or len(k) != 1 or not isinstance(v, str)
                       or not v.strip() or v.strip().casefold() == "none" for k, v in choices.items())):
            raise ValueError(f"{row['id']}: questão ou gabarito inválido")
        return
    tools, gold = row.get("tools"), row.get("gold_calls")
    if not isinstance(row.get("query"), str) or not isinstance(tools, list) or not tools or not isinstance(gold, list):
        raise ValueError(f"{row['id']}: exemplo de decisão inválido")
    names = set()
    for tool in tools:
        if (not isinstance(tool, dict) or not isinstance(tool.get("name"), str)
                or not tool["name"] or tool["name"] in names
                or not isinstance(tool.get("parameters", {}).get("properties"), dict)):
            raise ValueError(f"{row['id']}: definição de ferramenta inválida")
        names.add(tool["name"])
    if any(not isinstance(g, dict) or g.get("name") not in names
           or not isinstance(g.get("arguments"), dict) for g in gold):
        raise ValueError(f"{row['id']}: chamada do gabarito inválida")


def ids_for(rows):
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("IDs duplicados")
    return ids


def load_snapshot(directory=DEFAULT_DATA):
    lock = json.loads(LOCK.read_bytes())
    bundle = {}
    for name, spec in lock["datasets"].items():
        path = directory / spec["file"]
        content = checked_bytes(path.read_bytes(), spec)
        rows = parse_jsonl(content, str(path))
        for row in rows:
            validate_row(row, spec["track"], ("dev", "test"))
            provenance = row["provenance"]
            if (row["dataset"], row["sector"], provenance["source"], provenance["source_version"]) != (
                name, spec["sector"], spec["source"], spec["source_revision"]
            ):
                raise ValueError(f"{row['id']}: procedência incompatível com o snapshot")
        if Counter(row["split"] for row in rows) != spec["split_counts"]:
            raise ValueError(f"{name}: contagem por split divergente")
        if "category_counts" in spec:
            categories = Counter(row["source_id"].rsplit("_", 1)[0] for row in rows)
            if categories != spec["category_counts"]:
                raise ValueError(f"{name}: cotas divergentes")
        bundle[name] = (path, spec["track"], content, rows)
    rows = [row for _, _, _, records in bundle.values() for row in records]
    ids_for(rows)
    dev = [row for row in rows if row["split"] == "dev"]
    test = [row for row in rows if row["split"] == "test"]
    if groups(dev) & groups(test) or tool_names(dev) & tool_names(test):
        raise ValueError("Sobreposição de grupos ou ferramentas entre dev e teste")
    if find_duplicates(dev, test):
        raise ValueError("Textos iguais ou quase iguais entre dev e teste")
    return bundle


def groups(rows):
    return {(row["dataset"], row["group_id"]) for row in rows}


def tool_names(rows):
    return {tool["name"] for row in rows for tool in row.get("tools", [])}


def install_snapshot(source, destination):
    lock = json.loads(LOCK.read_bytes())
    if destination.exists():
        load_snapshot(destination)
        return
    with new_directory(destination) as stage:
        folder = source / "data/benchmark"
        if source.is_dir():
            for spec in lock["datasets"].values():
                name = spec["file"]
                (stage / name).write_bytes(checked_bytes((folder / name).read_bytes(), spec))
        else:
            prefix = f"Lumi-Benchmark-{lock['commit']}/data/benchmark"
            with ZipFile(source) as archive:
                for spec in lock["datasets"].values():
                    name = spec["file"]
                    (stage / name).write_bytes(checked_bytes(archive.read(f"{prefix}/{name}"), spec))
        load_snapshot(stage)


def source_keys(rows, field):
    return {(row["provenance"]["source"], row[field]) for row in rows
            if row.get("provenance", {}).get("source") and row.get(field)}


def audit_train(train, evaluation):
    """Lista colisões com dev/test, sem alterar os arquivos ou os splits."""
    train_ids, eval_ids = set(ids_for(train)), set(ids_for(evaluation))
    test = [row for row in evaluation if row["split"] == "test"]
    dev = [row for row in evaluation if row["split"] == "dev"]
    duplicates = sorted(find_duplicates(train, evaluation))
    return {
        "shared_ids": sorted(train_ids & eval_ids),
        "shared_groups": [list(group) for group in sorted(groups(train) & groups(evaluation))],
        "shared_source_ids": [list(key) for key in sorted(source_keys(train, "source_id")
                                                         & source_keys(evaluation, "source_id"))],
        "shared_source_groups": [list(key) for key in sorted(source_keys(train, "group_id")
                                                            & source_keys(evaluation, "group_id"))],
        "near_duplicates": [list(pair) for pair in duplicates],
        "reserved_tools": sorted(tool_names(train) & (tool_names(test) - tool_names(dev))),
    }


def load_demo():
    bundle = {}
    for track in TRACKS:
        path = ROOT / "data/examples" / f"{track}.jsonl"
        content = path.read_bytes()
        bundle[f"demo_{track}"] = (path, track, content, parse_jsonl(content, str(path)))
    return bundle
