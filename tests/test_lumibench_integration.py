import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class IntegrationTests(unittest.TestCase):
    def cli(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, "-m", "benchmark", *map(str, args)],
            cwd=ROOT, capture_output=True, text=True,
        )
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_demo_replay_keeps_missing_item_in_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            run, replay = Path(tmp) / "run", Path(tmp) / "replay"
            self.cli("run", "--suite", "demo", "--out", run)
            metrics = json.loads((run / "metricas.json").read_text())
            self.assertEqual(metrics["conhecimento"]["geral"]["accuracy"], 0.5)
            self.assertEqual(metrics["decisao"]["geral"]["call_exact_match"], 0.5)
            file = run / "predicoes_conhecimento.jsonl"
            first, second = file.read_text().splitlines()
            self.assertEqual(json.loads(first)["raw_output"], "Resposta: A")
            file.write_text(second + "\n")
            self.cli("score", "--run", run, "--out", replay)
            scored = json.loads((replay / "metricas.json").read_text())["conhecimento"]["geral"]
            self.assertEqual((scored["n"], scored["accuracy"], scored["missing_predictions"]), (2, 0, 1))

    def test_demo_run_never_overwrites_existing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            self.cli("run", "--suite", "demo", "--out", run)
            manifest = (run / "manifest.json").read_bytes()
            self.cli("run", "--suite", "demo", "--out", run, ok=False)
            self.assertEqual((run / "manifest.json").read_bytes(), manifest)

    def test_tools_are_scored_offline_and_schema_invalid_is_reported(self):
        from benchmark.toolcall import evaluate_decision
        example = {
            "tools": [{"name": "buscar", "parameters": {
                "properties": {"id": {"type": "integer"}}, "required": ["id"]}}],
            "gold_calls": [{"name": "buscar", "arguments": {"id": 1}}],
        }
        score = evaluate_decision('{"calls":[{"name":"buscar","arguments":{"id":"1"}}]}', example)
        self.assertFalse(score["schema_ok"])
        self.assertEqual(score["pred_calls"], [{"name": "buscar", "arguments": {"id": "1"}}])

    def test_snapshot_rejects_changed_bytes_but_accepts_historical_crlf(self):
        from benchmark.data import checked_bytes
        import hashlib
        lf = b'{"id":"a"}\n'
        crlf = lf.replace(b"\n", b"\r\n")
        spec = {key: hashlib.sha256(value).hexdigest()
                for key, value in [("sha256", lf), ("sha256_upstream_crlf", crlf)]}
        self.assertEqual(checked_bytes(crlf, spec), lf)
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            checked_bytes(lf.replace(b"a", b"b"), spec)

    def test_train_audit_catches_ids_groups_near_text_and_reserved_tools(self):
        from benchmark.data import audit_train
        query = "qual e a previsao do tempo em goiania neste fim de semana"
        dev = {"id": "a", "dataset": "d", "split": "dev", "group_id": "g", "question": "Exemplo A"}
        test = {"id": "b", "dataset": "e", "split": "test", "group_id": "h", "query": query,
                "tools": [{"name": "previsao"}]}
        train = [
            dict(dev, split="train", question="outro enunciado"),
            dict(dev, id="c", dataset="f", split="train", group_id="z", question=query + " agora"),
            dict(test, id="d", split="train", group_id="j", query="outro pedido"),
        ]
        findings = audit_train(train, [dev, test])
        self.assertEqual(findings["shared_ids"], ["a"])
        self.assertEqual(findings["shared_groups"], [["d", "g"]])
        self.assertEqual(findings["near_duplicates"], [["c", "b", 0.889]])
        self.assertEqual(findings["reserved_tools"], ["previsao"])

    def test_http_backend_sends_no_gold_and_preserves_raw_and_structured_output(self):
        from io import BytesIO
        from unittest.mock import patch
        from adapters.backends import OpenAICompatBackend
        from benchmark.run import predict

        backend = OpenAICompatBackend("http://localhost:8000/v1", "example")
        example = {
            "id": "d",
            "query": "Cheque o pedido",
            "tools": [{"name": "pedido", "description": "Consulta um pedido",
                       "parameters": {"type": "object", "properties": {"id": {"type": "integer"}}}}],
            "gold_calls": [{"name": "pedido", "arguments": {"id": 49182}}],
        }
        structured = [{"type": "function", "function": {"name": "pedido", "arguments": '{"id":42}'}}]
        response = {"choices": [{"message": {"content": "<bos>Vou consultar.", "tool_calls": structured}}],
                    "usage": {"completion_tokens": 8}}
        with patch("urllib.request.urlopen", return_value=BytesIO(json.dumps(response).encode())) as transport:
            row = predict(backend, "decisao", example, "direct", "default",
                          {"max_new_tokens": 32, "temperature": 0, "seed": 42})
        request = transport.call_args.args[0]
        self.assertNotIn(b"49182", request.data)
        self.assertNotIn(b"gold_calls", request.data)
        self.assertIn(b"Cheque o pedido", request.data)
        self.assertEqual(row["raw_output"], "<bos>Vou consultar.")
        self.assertEqual(row["tool_calls"], structured)
        self.assertEqual(row["n_gen_tokens"], 8)
        self.assertEqual(json.loads(row["normalized_output"]), {"tool_calls": structured})

    def test_audit_matches_original_id_even_if_candidate_changes_dataset_label(self):
        from benchmark.data import audit_train

        example = {"id": "item-a", "dataset": "a", "group_id": "grp", "split": "test",
                   "question": "Original", "source_id": "source-a",
                   "provenance": {"source": "origin/dataset"}}
        candidate = dict(example, dataset="renamed", id="local-id", split="train", question="Reescrita")
        findings = audit_train([candidate], [example])
        self.assertEqual(findings["shared_source_ids"], [["origin/dataset", "source-a"]])
        self.assertEqual(findings["shared_source_groups"], [["origin/dataset", "grp"]])

    def test_train_example_requires_source_metadata(self):
        from benchmark.data import validate_row
        row = {"id": "x", "dataset": "d", "source_id": "orig-1", "group_id": "g", "sector": "geral",
               "task": "mcq", "split": "train", "question": "Exemplo", "choices": {"A": "Um", "B": "Dois"},
               "answer": "A"}
        with self.assertRaisesRegex(ValueError, "procedência"):
            validate_row(row, "conhecimento", ("train",))
        row["provenance"] = {"source": "test/origem", "source_version": "v1", "license": "CC0-1.0",
                             "language_origin": "sintetico", "transformations": []}
        validate_row(row, "conhecimento", ("train",))
