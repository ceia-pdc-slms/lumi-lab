"""CLI do LumiBench no Lumi Lab."""

import argparse
import json
from pathlib import Path
from subprocess import CalledProcessError
from zipfile import BadZipFile

from . import baseline, data, run


def main(argv=None):
    parser = argparse.ArgumentParser(description="Importação, execução e auditoria do LumiBench")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="obtém o avaliador e valida os dados da versão publicada")
    install = commands.add_parser("import", help="instala o snapshot do ZIP ou checkout fixado")
    install.add_argument("--source", type=Path, required=True)

    validate = commands.add_parser("validate", help="valida os cinco datasets instalados")
    evaluate = commands.add_parser("run", help="executa um perfil e pontua as predições")
    selection = evaluate.add_mutually_exclusive_group()
    selection.add_argument("--model", choices=("lumi", "qwen3"), help="usa o perfil Ollama direct publicado")
    selection.add_argument("--config", type=Path, help="usa uma configuração do avaliador integrado")
    evaluate.add_argument("--suite", choices=("lumibench", "demo"), default="lumibench")
    evaluate.add_argument("--split", choices=("dev", "test"))
    evaluate.add_argument("--dataset", action="append", default=[])
    evaluate.add_argument("--limit-per-dataset", type=int)
    evaluate.add_argument("--limit", type=int, help="limite por trilha no perfil Ollama, em dev")
    evaluate.add_argument("--out", type=Path, required=True)

    compare = commands.add_parser("compare", help="recalcula e compara duas execuções do perfil publicado")
    compare.add_argument("--split", choices=("dev", "test"), required=True)
    compare.add_argument("--lumi", type=Path, required=True)
    compare.add_argument("--qwen3", type=Path, required=True)

    score = commands.add_parser("score", help="recalcula resultados offline")
    score.add_argument("--run", type=Path, required=True)
    score.add_argument("--out", type=Path, required=True)
    audit = commands.add_parser("audit-train", help="verifica candidatos de treino contra dev/test")
    audit.add_argument("--candidates", type=Path, required=True)

    for command in (prepare, evaluate, compare):
        command.add_argument("--benchmark", choices=(data.BENCHMARK_ID,), default=data.BENCHMARK_ID)
        command.add_argument("--source", type=Path, help="checkout da revisão do avaliador upstream")
    for command in (prepare, install, validate, evaluate, compare, score, audit):
        command.add_argument("--data-dir", type=Path, default=data.DEFAULT_DATA)

    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            baseline.prepare(args.source or baseline.SOURCE, args.data_dir)
        elif args.command == "import":
            data.install_snapshot(args.source, args.data_dir)
            print(args.data_dir)
        elif args.command == "validate":
            bundle = data.load_snapshot(args.data_dir)
            counts = {}
            for name, (_, _, _, rows) in bundle.items():
                counts[name] = {split: sum(row["split"] == split for row in rows) for split in ("dev", "test")}
            print(json.dumps(counts, indent=2))
        elif args.command == "run":
            if args.model:
                if args.split is None:
                    evaluate.error("--model exige --split")
                if args.suite != "lumibench" or args.dataset or args.limit_per_dataset is not None:
                    evaluate.error("--suite demo, --dataset e --limit-per-dataset usam o avaliador integrado")
                baseline.execute(args.source or baseline.SOURCE, args.data_dir, args.out,
                                 args.model, args.split, args.limit)
            else:
                if args.source is not None or args.limit is not None:
                    evaluate.error("--source e --limit exigem --model")
                print(run.execute(args.config or run.DEFAULT_CONFIG, args.out, suite=args.suite,
                                  directory=args.data_dir, split=args.split or "dev",
                                  datasets=args.dataset, limit=args.limit_per_dataset))
        elif args.command == "compare":
            summary = baseline.compare(args.source or baseline.SOURCE, args.data_dir,
                                       args.split, args.lumi, args.qwen3)
            print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))
        elif args.command == "score":
            print(run.replay(args.run, args.out, directory=args.data_dir))
        else:
            evaluation = [row for _, _, _, rows in data.load_snapshot(args.data_dir).values() for row in rows]
            content = args.candidates.read_bytes()
            train = data.parse_jsonl(content, str(args.candidates))
            if not train:
                raise ValueError("Arquivo de candidatos vazio")
            for row in train:
                data.validate_row(row, data.row_track(row), ("train",))
            findings = data.audit_train(train, evaluation)
            print(json.dumps({
                "n_candidates": len(train),
                "candidate_sha256": data.digest(content),
                "evaluation_commit": json.loads(data.LOCK.read_bytes())["commit"],
                **findings,
            }, ensure_ascii=False, indent=2))
            return int(any(findings.values()))
    except (ValueError, OSError, KeyError, TypeError, AttributeError, BadZipFile, CalledProcessError) as exc:
        parser.exit(2, f"Erro: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
