"""Metricas e agregacao. Python puro (sem numpy)."""
import math
from collections import defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def percentile(xs, q):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    f, c = math.floor(k), math.ceil(k)
    return xs[f] if f == c else xs[f] + (xs[c] - xs[f]) * (k - f)


# ------------------------------------------------------------ trilha A
def mcq_summary(rows):
    """rows: dicts com correct (bool), valid (bool). Invalida conta como erro em accuracy."""
    n = len(rows)
    k = sum(1 for r in rows if r["correct"])
    v = sum(1 for r in rows if r["valid"])
    lo, hi = wilson(k, n)
    return {"n": n, "accuracy": k / n if n else float("nan"), "ci95": (lo, hi),
            "validity": v / n if n else float("nan"),
            "accuracy_on_valid": (k / v) if v else float("nan")}


# ------------------------------------------------------------ trilha B
def decision_summary(rows):
    n = len(rows)
    def rate(f):
        return sum(1 for r in rows if r[f]) / n if n else float("nan")
    tot = sum(r["n_arg_total"] for r in rows)
    good = sum(r["n_arg_correct"] for r in rows)
    no_call = [r for r in rows if r["gold_is_no_call"]]
    call = [r for r in rows if not r["gold_is_no_call"]]
    return {"n": n, "format_valid": rate("format_ok"), "schema_valid": rate("schema_ok"),
            "tool_accuracy": rate("name_ok"), "args_accuracy_per_arg": (good / tot) if tot else float("nan"),
            "call_exact_match": rate("exact"),
            "abstention_accuracy": (sum(1 for r in no_call if r["exact"]) / len(no_call)) if no_call else float("nan"),
            "abstention_accuracy_lenient": (sum(1 for r in no_call if r["lenient_no_call"]) / len(no_call)) if no_call else float("nan"),
            "false_call_rate": (sum(1 for r in no_call if not r["exact"] and r["format_ok"]) / len(no_call)) if no_call else float("nan"),
            "missed_call_rate": (sum(1 for r in call if r.get("missed_call", False)) / len(call)) if call else float("nan"),
            "n_call": len(call), "n_no_call": len(no_call)}


def efficiency(rows):
    lat = [r["latency_s"] for r in rows if r.get("latency_s") is not None]
    tok = [r["n_gen_tokens"] for r in rows if r.get("n_gen_tokens") is not None]
    tps = [r["n_gen_tokens"] / r["latency_s"] for r in rows
           if r.get("n_gen_tokens") is not None and (r.get("latency_s") or 0) > 0]
    return {"latency_p50_s": percentile(lat, .5), "latency_p95_s": percentile(lat, .95),
            "tokens_mean": sum(tok) / len(tok) if tok else float("nan"),
            "tokens_p95": percentile(tok, .95), "tokens_per_s_mean": sum(tps) / len(tps) if tps else float("nan")}


def group_by(rows, key):
    out = defaultdict(list)
    for r in rows:
        out[r[key]].append(r)
    return dict(out)
