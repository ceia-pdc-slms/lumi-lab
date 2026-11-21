"""Verificação textual de sobreposição via Jaccard de 5-gramas."""
import re
import unicodedata
from collections import defaultdict


def norm_text(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).casefold()
    return re.sub(r"\W+", " ", s).strip()


def text_key(r):
    return norm_text(r.get("question") or r.get("query") or "")


def shingles(text, k=5):
    w = text.split()
    return {" ".join(w[i:i + k]) for i in range(max(1, len(w) - k + 1))}


def find_duplicates(a, b, threshold=0.8):
    """Pares (id_a, id_b) iguais (hash exato) ou quase iguais (Jaccard de shingles >= threshold)."""
    idx, sh_b = defaultdict(set), {}
    for r in b:
        sh = shingles(text_key(r)); sh_b[r["id"]] = sh
        for s in sh:
            idx[s].add(r["id"])
    out = []
    for r in a:
        sa = shingles(text_key(r))
        cand = set().union(*(idx.get(s, set()) for s in sa)) if sa else set()
        for bid in cand:
            sb = sh_b[bid]
            j = len(sa & sb) / len(sa | sb)
            if j >= threshold:
                out.append((r["id"], bid, round(j, 3)))
    return out
