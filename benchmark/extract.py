"""Extracao e normalizacao da resposta de multipla escolha (trilha conhecimento).

Regras (ordem de prioridade; vale a ULTIMA ocorrencia, para ignorar letras citadas durante o raciocinio):
 1. \\boxed{X}
 2. marcador explicito: "Resposta: X", "a alternativa correta e X", "gabarito: X", "letra X"
 3. texto inteiro e so a letra: "B", "(B)", "B."
 4. texto comeca com "B)" / "B." / "B:" (alternativa seguida do texto)
Se nada casar, ou a letra extraida nao esta entre as alternativas validas: resposta INVALIDA (None).
"""
import re

_THINK = re.compile(r"<think>.*?(?:</think>|\Z)", re.S | re.I)
_BOXED = re.compile(r"\\boxed\{\s*\(?([A-J])\)?\s*\}")
_MARK = re.compile(
    r"(?i:resposta|alternativa|gabarito|answer|letra|op[cç][aã]o)"
    r"(?i:\s+(?:final|correta|certa))?\s*(?i:[:=\-]|é|e|eh|is|seria)?\s*"
    r"(?i:a\s+)?(?i:letra\s+|alternativa\s+|op[cç][aã]o\s+)?\(?\**([A-J])\b(?![a-zà-úA-Z])"
)
_ONLY = re.compile(r"^\W*([A-J])\W*$")
_START = re.compile(r"^\W*([A-J])\s*[\).:\-]\s+\S")


def strip_reasoning(text: str) -> str:
    return _THINK.sub(" ", text or "").strip()


def extract_choice(text: str, valid: str = "ABCDE"):
    """Retorna (letra | None, como). `como` descreve a regra usada (util para auditoria)."""
    t = strip_reasoning(text)
    if not t:
        return None, "empty"
    for name, rx in (("boxed", _BOXED), ("marker", _MARK)):
        ms = rx.findall(t)
        if ms:
            letter = ms[-1]
            return (letter, name) if letter in valid else (None, f"{name}_out_of_range")
    m = _ONLY.match(t)
    if m:
        letter = m.group(1)
        return (letter, "only_letter") if letter in valid else (None, "only_letter_out_of_range")
    m = _START.match(t)
    if m:
        letter = m.group(1)
        return (letter, "leading_letter") if letter in valid else (None, "leading_out_of_range")
    return None, "no_match"
