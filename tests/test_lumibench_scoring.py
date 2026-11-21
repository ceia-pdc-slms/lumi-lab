import json
import unittest

from benchmark import extract, toolcall


class TestExtract(unittest.TestCase):
    def test_cases(self):
        E = extract.extract_choice
        self.assertEqual(E("Resposta: B")[0], "B")
        self.assertEqual(E("Considerando A e C, descarto-as.\nResposta final: D", "ABCD")[0], "D")
        self.assertEqual(E("A resposta correta é a letra C.")[0], "C")
        self.assertEqual(E("\\boxed{D}")[0], "D")
        self.assertEqual(E("(B)")[0], "B")
        self.assertEqual(E("B) Inibidores da ECA")[0], "B")
        self.assertEqual(E("<think>talvez A</think>Resposta: C")[0], "C")
        self.assertIsNone(E("a resposta nao esta clara")[0])
        self.assertIsNone(E("Resposta: E", "ABCD")[0])
        self.assertIsNone(E("")[0])


class TestToolcall(unittest.TestCase):
    TOOLS = [{"name": "calcular_imc", "description": "", "parameters": {"type": "object", "properties": {"peso_kg": {"type": "number"}, "altura_m": {"type": "number"}}, "required": ["peso_kg", "altura_m"]}},
             {"name": "consultar_clima", "description": "", "parameters": {"type": "object", "properties": {"municipio": {"type": "string"}, "uf": {"type": "string"}, "dias": {"type": "integer", "default": 1}}, "required": ["municipio", "uf"]}},
             {"name": "calculadora", "description": "", "parameters": {"type": "object", "properties": {"expressao": {"type": "string"}}, "required": ["expressao"]}}]
    def ex(self, gold): return {"tools": self.TOOLS, "gold_calls": gold}

    def test_parse_formats(self):
        P = toolcall.parse_calls
        self.assertEqual(P('{"calls":[{"name":"f","arguments":{"a":1}}]}')[0], [{"name": "f", "arguments": {"a": 1}}])
        self.assertEqual(P('[{"name":"f","arguments":{}}]')[1], "json")
        self.assertEqual(P('<tool_call>{"name":"f","arguments":{"a":2}}</tool_call>')[0][0]["arguments"], {"a": 2})
        self.assertEqual(P('Claro! {"calls":[{"name":"f","arguments":{"a":1}}]} pronto')[1], "json_embedded")
        self.assertEqual(P('[f(a=1, b="x"), g(c=2)]')[0][1], {"name": "g", "arguments": {"c": 2}})
        self.assertEqual(P('{"calls": []}')[0], [])
        self.assertEqual(P('{"name":"f","arguments":"{\\"a\\": 1}"}')[0][0]["arguments"], {"a": 1})
        self.assertIsNone(P("nao preciso de ferramenta")[0])

    def test_exact_and_errors(self):
        g = [{"name": "calcular_imc", "arguments": {"peso_kg": 82, "altura_m": 1.75}}]
        E = lambda raw, gold=g: toolcall.evaluate_decision(raw, self.ex(gold))
        self.assertTrue(E('{"calls":[{"name":"calcular_imc","arguments":{"peso_kg":82,"altura_m":1.75}}]}')["exact"])
        self.assertTrue(E('{"calls":[{"name":"calcular_imc","arguments":{"peso_kg":"82","altura_m":"1,75"}}]}')["args_ok"])  # coerção numérica
        r = E('{"calls":[{"name":"calcular_imc","arguments":{"peso_kg":82,"altura_m":1.57}}]}')
        self.assertTrue(r["name_ok"]); self.assertFalse(r["args_ok"]); self.assertEqual((r["n_arg_correct"], r["n_arg_total"]), (1, 2))
        r = E('{"calls":[{"name":"calcular_imc","arguments":{"peso_kg":82,"altura_m":1.75,"idade":30}}]}')
        self.assertFalse(r["schema_ok"]); self.assertFalse(r["exact"])  # argumento inventado
        r = E('{"calls":[{"name":"consultar_clima","arguments":{"municipio":"x","uf":"GO"}}]}')
        self.assertFalse(r["name_ok"])
        self.assertFalse(E("texto livre")["format_ok"])

    def test_parallel_order_free_and_accents(self):
        g = [{"name": "consultar_clima", "arguments": {"municipio": "Goiânia", "uf": "GO", "dias": 3}},
             {"name": "consultar_clima", "arguments": {"municipio": "Cuiabá", "uf": "MT", "dias": 3}}]
        raw = json.dumps({"calls": [{"name": "consultar_clima", "arguments": {"municipio": "cuiaba", "uf": "mt", "dias": 3}},
                                    {"name": "consultar_clima", "arguments": {"municipio": "Goiania", "uf": "GO", "dias": 3}}]})
        self.assertTrue(toolcall.evaluate_decision(raw, self.ex(g))["exact"])
        one = json.dumps({"calls": [json.loads(raw)["calls"][0]]})
        self.assertFalse(toolcall.evaluate_decision(one, self.ex(g))["exact"])

    def test_no_call(self):
        e = self.ex([])
        self.assertTrue(toolcall.evaluate_decision('{"calls": []}', e)["exact"])
        r = toolcall.evaluate_decision('{"calls":[{"name":"calculadora","arguments":{"expressao":"1+1"}}]}', e)
        self.assertFalse(r["exact"]); self.assertTrue(r["false_call"])
        r = toolcall.evaluate_decision("Nao ha ferramenta adequada para isso.", e)
        self.assertFalse(r["exact"]); self.assertTrue(r["lenient_no_call"])  # estrito erra, leniente aceita prosa

    def test_math_expr_rule(self):
        g = [{"name": "calculadora", "arguments": {"expressao": "(125 * 4) + 18 / 3"}, "arg_rules": {"expressao": "math_expr"}}]
        self.assertTrue(toolcall.evaluate_decision('{"calls":[{"name":"calculadora","arguments":{"expressao":"125*4+6"}}]}', self.ex(g))["exact"])
        self.assertFalse(toolcall.evaluate_decision('{"calls":[{"name":"calculadora","arguments":{"expressao":"125*4+7"}}]}', self.ex(g))["exact"])
        self.assertFalse(toolcall.values_equal("__import__('os')", "1", "math_expr"))

    def test_optional_default_not_penalized(self):
        g = [{"name": "consultar_clima", "arguments": {"municipio": "Goiânia", "uf": "GO"}}]
        raw = '{"calls":[{"name":"consultar_clima","arguments":{"municipio":"Goiânia","uf":"GO","dias":1}}]}'
        self.assertTrue(toolcall.evaluate_decision(raw, self.ex(g))["exact"])  # dias=1 e o default do schema
        raw = raw.replace('"dias":1', '"dias":5')
        self.assertFalse(toolcall.evaluate_decision(raw, self.ex(g))["exact"])


class TestReport(unittest.TestCase):
    def test_tokens_per_second_uses_pairs_from_the_same_example(self):
        from benchmark.metrics import efficiency
        result = efficiency([
            {"n_gen_tokens": None, "latency_s": 1},
            {"n_gen_tokens": 20, "latency_s": 4},
            {"n_gen_tokens": 100, "latency_s": None},
        ])
        self.assertEqual(result["tokens_per_s_mean"], 5)

    def test_inference_failure_remains_an_error_even_with_valid_response_text(self):
        from benchmark.report import score_rows, summarize
        example = {"id": "x", "dataset": "d", "sector": "geral", "task": "mcq",
                   "choices": {"A": "certa", "B": "errada"}, "answer": "A"}
        rows = score_rows("conhecimento", [example], [
            {"id": "x", "raw_output": "Resposta: A", "error": "TimeoutError"}
        ], "default")
        summary = summarize("conhecimento", rows)
        self.assertEqual((summary["n"], summary["accuracy"], summary["inference_failures"]), (1, 0, 1))

    def test_malformed_call_does_not_salvage_one_valid_child_or_unrelated_empty_array(self):
        responses = [
            '{"calls":[{"name":"f","arguments":{}},{"name":7,"arguments":{}}]}',
            '{"calls":[{"name":7,"arguments":{}}],"unused":[]}',
            'Segue: {"calls":[{"name":"f","arguments":{}},{"name":7,"arguments":{}}]}',
            'Segue: {"calls":[{"name":"f","arguments":{}}',
        ]
        for response in responses:
            with self.subTest(response=response):
                self.assertIsNone(toolcall.parse_calls(response)[0])

    def test_empty_structured_calls_do_not_discard_textual_calls(self):
        from adapters.outputs import adapt
        text = '{"calls":[{"name":"f","arguments":{}}]}'
        self.assertEqual(adapt("default", "decisao", text, []), text)
        self.assertEqual(toolcall.parse_calls(adapt("default", "decisao", "", []))[0], [])

    def test_reasoning_without_final_answer_does_not_score_as_response(self):
        from adapters.outputs import adapt
        self.assertIsNone(extract.extract_choice("<think>minha hipótese é Resposta: B")[0])
        text = adapt("reasoning", "conhecimento", "<think>Resposta final: B</think>")
        self.assertIsNone(extract.extract_choice(text)[0])
        self.assertIsNone(toolcall.parse_calls('<think>exemplo: {"calls": []}')[0])
