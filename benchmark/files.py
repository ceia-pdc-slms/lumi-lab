"""Leitura e escrita dos artefatos da avaliação."""

import json
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


@contextmanager
def new_directory(destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f"Diretório já existe: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent, prefix=".lumibench-") as temporary:
        stage = Path(temporary) / "artifacts"
        stage.mkdir()
        yield stage
        stage.rename(destination)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
