import unittest

from adapters.choice_service import parse_request, port_for, require_model


class ChoiceServiceTests(unittest.TestCase):
    def test_endpoint_accepts_only_plain_ipv4_loopback(self):
        self.assertEqual(port_for("http://127.0.0.1:11440"), 11440)
        for url in ("https://127.0.0.1:11440", "http://192.168.0.4:80",
                    "http://127.0.0.1:11440/other", "http://user@127.0.0.1:11440"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                port_for(url)

    def test_request_uses_one_user_message_and_only_supported_labels(self):
        messages = [{"role": "user", "content": "Pergunta"}]
        self.assertEqual(parse_request({"messages": messages, "choice_letters": "AB"}), (messages, "AB"))
        for payload in ({"messages": messages, "choice_letters": "AA"},
                        {"messages": messages, "choice_letters": "AZ"},
                        {"messages": [{"role": "system", "content": "Pergunta"}], "choice_letters": "AB"}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse_request(payload)

    def test_model_must_match_weights_tokenizer_and_template(self):
        model = {"revision": "a", "tokenizer_revision": "a", "chat_template_sha256": "b"}
        require_model(model, model)
        with self.assertRaisesRegex(ValueError, "chat_template_sha256"):
            require_model(model, {**model, "chat_template_sha256": "c"})
