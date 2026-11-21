import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


class BaselinePredictionsTests(unittest.TestCase):
    def test_requires_exact_item_order_and_coverage(self):
        from benchmark.baseline import read_predictions

        with TemporaryDirectory() as temporary:
            predictions = Path(temporary) / "predicoes.jsonl"
            for ids in (["b", "a"], ["a"], ["a", "a"]):
                with self.subTest(ids=ids):
                    predictions.write_text("".join(json.dumps({"id": item}) + "\n" for item in ids))
                    with self.assertRaisesRegex(ValueError, "IDs"):
                        read_predictions(predictions, ["a", "b"])
            predictions.write_text('{"id":"a"}\n{"id":"b"}\n')
            self.assertEqual(read_predictions(predictions, ["a", "b"]), [{"id": "a"}, {"id": "b"}])


class CatalogCliTests(unittest.TestCase):
    def test_public_cli_routes_prepare_run_and_compare(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch

        from benchmark import baseline
        from benchmark.__main__ import main

        source, data_dir = Path("upstream"), Path("snapshot")
        options = ["--benchmark", "lumibench/v1", "--source", str(source), "--data-dir", str(data_dir)]
        with patch.object(baseline, "prepare") as prepare:
            self.assertEqual(main(["prepare", *options]), 0)
            prepare.assert_called_once_with(source, data_dir)
        with patch.object(baseline, "execute") as execute:
            self.assertEqual(main(["run", *options, "--model", "lumi", "--split", "test", "--out", "run"]), 0)
            execute.assert_called_once_with(source, data_dir, Path("run"), "lumi", "test", None)
        with patch.object(baseline, "compare", return_value={"split": "test"}) as compare:
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["compare", *options, "--split", "test", "--lumi", "l", "--qwen3", "q"]), 0)
            compare.assert_called_once_with(source, data_dir, "test", Path("l"), Path("q"))
            self.assertEqual(json.loads(output.getvalue()), {"split": "test"})

    def test_published_model_requires_an_explicit_split_and_rejects_native_options(self):
        from contextlib import redirect_stderr
        from io import StringIO

        from benchmark.__main__ import main

        with redirect_stderr(StringIO()):
            for options in ([], ["--split", "dev", "--dataset", "bluex"]):
                with self.subTest(options=options), self.assertRaises(SystemExit) as error:
                    main(["run", "--model", "lumi", "--out", "run", *options])
                self.assertEqual(error.exception.code, 2)
