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
