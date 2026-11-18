import unittest

from adapters.choice_logits import choose_letter


class ChoiceLogitsTests(unittest.TestCase):
    def test_chooses_largest_valid_logit_and_preserves_negative_scores(self):
        self.assertEqual(choose_letter("ABC", {"A": -5.0, "B": -1.0, "C": -2.0}), "B")

    def test_requires_a_finite_logit_for_every_allowed_alternative(self):
        for logits in ({"A": 1}, {"A": 1, "B": 2, "C": 9}, {"A": 1, "B": float("nan")}):
            with self.subTest(logits=logits), self.assertRaises(ValueError):
                choose_letter("AB", logits)

    def test_ties_use_order_of_presented_labels(self):
        self.assertEqual(choose_letter("AB", {"B": 1, "A": 1}), "A")
