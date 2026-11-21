"""Adaptadores: convertem a saida bruta de cada modelo para o texto que o avaliador le.

O avaliador sempre aplica `extract_choice` (trilha A) ou `parse_calls` (trilha B) sobre o resultado.
Para um modelo novo (ex.: Lumi Decision), registre um adaptador aqui em vez de mexer no avaliador:
as regras de correcao ficam iguais para todos os modelos.
"""
import json
import re

from benchmark.extract import strip_reasoning

_SPECIAL = re.compile(r"<\|[^|>]*\|>|</?s>|<eos>|<bos>")


def default(raw: str) -> str:
    return _SPECIAL.sub("", raw or "").strip()


def after_final_marker(raw: str) -> str:
    """Para modelos de reasoning: ignora a resolucao intermediaria e le so o que vem apos o ultimo marcador."""
    t = strip_reasoning(default(raw))
    parts = re.split(r"(?i)(?:resposta final|final answer)\s*[:\-]?", t)
    return ("Resposta: " + parts[-1].strip()) if len(parts) > 1 else t


ADAPTERS = {"default": default, "reasoning": after_final_marker}


def adapt(name, track, raw, tool_calls=None):
    if track == "decisao":
        text = default(raw)
        if tool_calls or (tool_calls == [] and not text):
            return json.dumps({"tool_calls": tool_calls}, ensure_ascii=False)
        return text
    return ADAPTERS[name](raw)
