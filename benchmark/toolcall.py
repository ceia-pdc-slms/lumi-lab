"""Parse e correcao de chamadas de ferramenta (trilha decisao agentica).

Nesta versao NAO executamos as ferramentas: comparamos a chamada produzida com a chamada esperada.
"""
import ast
import itertools
import json
import math
import re
import unicodedata

from .extract import strip_reasoning

_TOOLTAG = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.S | re.I)
_FENCE = re.compile(r"```(?:json|python|tool_code)?\s*(.*?)```", re.S | re.I)


# ---------------------------------------------------------------- parse
def _norm_call(obj):
    """Normaliza varios formatos de uma chamada para {'name', 'arguments'}."""
    if not isinstance(obj, dict):
        return None
    if "function" in obj and isinstance(obj["function"], dict):
        obj = obj["function"]
    name = obj.get("name") or obj.get("tool") or obj.get("function_name")
    args = obj.get("arguments", obj.get("parameters", obj.get("args", {})))
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            return None
    if not isinstance(name, str) or not isinstance(args, dict):
        return None
    return {"name": name, "arguments": args}


def _from_json_obj(obj):
    if isinstance(obj, list):
        calls = [_norm_call(o) for o in obj]
        return None if any(c is None for c in calls) else calls
    if isinstance(obj, dict):
        for k in ("calls", "tool_calls", "function_calls"):
            if k in obj and isinstance(obj[k], list):
                return _from_json_obj(obj[k])
        c = _norm_call(obj)
        return [c] if c else None
    return None


def _balanced(text):
    """Encontra blocos externos completos sem extrair filhos de um JSON inválido."""
    closing = []
    in_string = escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char in "{[":
            if not closing:
                start = index
            closing.append("}" if char == "{" else "]")
        elif closing and char == '"':
            in_string = True
        elif closing and char in "}]":
            if closing.pop() != char:
                return
            if not closing:
                yield text[start:index + 1]


def _python_style(text):
    """Formato BFCL: [func(a=1, b="x"), g(c=2)] ou func(a=1)."""
    try:
        node = ast.parse(text.strip(), mode="eval").body
    except SyntaxError:
        return None
    nodes = node.elts if isinstance(node, ast.List) else [node]
    calls = []
    for n in nodes:
        if not isinstance(n, ast.Call) or n.args:
            return None
        name = ast.unparse(n.func)
        try:
            args = {k.arg: ast.literal_eval(k.value) for k in n.keywords}
        except Exception:
            return None
        calls.append({"name": name, "arguments": args})
    return calls


def parse_calls(raw: str):
    """Retorna (lista_de_chamadas | None, formato). None = nao foi possivel interpretar."""
    t = strip_reasoning(raw)
    if not t:
        return None, "empty"
    tags = _TOOLTAG.findall(t)
    if tags:
        calls = []
        for s in tags:
            try:
                c = _from_json_obj(json.loads(s))
            except Exception:
                return None, "tool_call_tag_invalid"
            if c is None:
                return None, "tool_call_tag_invalid"
            calls += c
        return calls, "tool_call_tag"
    cands = [t] + _FENCE.findall(t)
    for cand in cands:
        try:
            obj = json.loads(cand)
        except (ValueError, RecursionError):
            continue
        calls = _from_json_obj(obj)
        return (calls, "json") if calls is not None else (None, "invalid_call_shape")
    for cand in cands:
        for piece in _balanced(cand):
            try:
                c = _from_json_obj(json.loads(piece))
            except Exception:
                continue
            if c is not None:
                return c, "json_embedded"
    for cand in cands:
        c = _python_style(cand)
        if c is not None:
            return c, "python_style"
    return None, "unparsed"


def looks_like_call(raw: str) -> bool:
    return bool(re.search(r'"(?:calls|name|tool_calls|function_calls)"\s*:|<tool_call>|\w+\s*\(\s*\w+\s*=',
                          strip_reasoning(raw)))


# ---------------------------------------------------------------- normalizacao e igualdade
def norm_str(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().strip(".,;:").casefold()


def _to_float(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        try:
            return float(x)
        except OverflowError:
            return None
    if isinstance(x, str):
        s = x.strip().replace("R$", "").replace(" ", "")
        if re.fullmatch(r"-?\d+,\d+", s):
            s = s.replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _safe_eval(expr):
    node = ast.parse(str(expr).replace("^", "**").replace(",", "."), mode="eval")
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float): return float(n.value)
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)):
            a, b = ev(n.left), ev(n.right)
            return {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b,
                    ast.Div: lambda: a / b, ast.Pow: lambda: math.pow(a, b), ast.Mod: lambda: a % b}[type(n.op)]()
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return -ev(n.operand) if isinstance(n.op, ast.USub) else ev(n.operand)
        raise ValueError("expressao nao permitida")
    return ev(node)


def values_equal(pred, gold, rule=None, accept=None):
    """Igualdade tolerante: numeros (tol. relativa 1e-6), strings sem acento/caixa, listas, dicts."""
    if rule == "math_expr":
        try:
            return math.isclose(_safe_eval(pred), _safe_eval(gold), rel_tol=1e-6, abs_tol=1e-9)
        except Exception:
            return False
    options = [gold] + list(accept or [])
    for g in options:
        if isinstance(g, bool) or isinstance(pred, bool):
            if isinstance(g, bool) and isinstance(pred, bool) and g == pred:
                return True
            continue
        gf, pf = _to_float(g), _to_float(pred)
        if gf is not None and pf is not None and isinstance(g, (int, float)):
            if math.isclose(gf, pf, rel_tol=1e-6, abs_tol=1e-9):
                return True
            continue
        if isinstance(g, str) and isinstance(pred, str):
            if norm_str(g) == norm_str(pred):
                return True
            continue
        if isinstance(g, list) and isinstance(pred, list) and len(g) == len(pred):
            if rule == "unordered":
                if all(any(values_equal(p, x) for p in pred) for x in g):
                    return True
            elif all(values_equal(p, x) for p, x in zip(pred, g)):
                return True
            continue
        if isinstance(g, dict) and isinstance(pred, dict) and set(g) == set(pred):
            if all(values_equal(pred[k], g[k]) for k in g):
                return True
    return False


# ---------------------------------------------------------------- validade (schema)
_TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}


def schema_errors(call, tools_by_name):
    """Lista de problemas de uma chamada em relacao ao schema da ferramenta."""
    tool = tools_by_name.get(call["name"])
    if tool is None:
        return ["ferramenta_inexistente"]
    params = tool.get("parameters", {})
    props, req = params.get("properties", {}), params.get("required", [])
    errs = []
    for k in req:
        if k not in call["arguments"]:
            errs.append(f"falta_obrigatorio:{k}")
    for k, v in call["arguments"].items():
        if k not in props:
            errs.append(f"argumento_inexistente:{k}")
            continue
        spec = props[k]
        ty = _TYPES.get(spec.get("type"))
        if ty is not None:
            ok = isinstance(v, ty) and not (spec["type"] in ("integer", "number") and isinstance(v, bool))
            if spec["type"] == "integer" and isinstance(v, float) and v.is_integer():
                ok = True
            if not ok:
                errs.append(f"tipo_invalido:{k}")
        if "enum" in spec and v not in spec["enum"]:
            errs.append(f"fora_do_enum:{k}")
    return errs


# ---------------------------------------------------------------- correcao
def _args_result(pred, gold, tool):
    """(n_corretos, n_total, todos_corretos). Argumento marcado em gold['optional'] e ausente na previsao nao conta como erro."""
    rules, accept = gold.get("arg_rules", {}), gold.get("accept", {})
    optional = set(gold.get("optional", []))
    props = (tool or {}).get("parameters", {}).get("properties", {})
    keys = set(gold["arguments"]) - {k for k in optional if k not in pred["arguments"]}
    good = sum(1 for k in keys if k in pred["arguments"] and
               values_equal(pred["arguments"][k], gold["arguments"][k], rules.get(k), accept.get(k)))
    extra_ok = True
    for k, v in pred["arguments"].items():
        if k not in gold["arguments"]:
            default = props.get(k, {}).get("default", object())
            if not (k in props and values_equal(v, default)):
                extra_ok = False
    return good, len(keys), (good == len(keys) and extra_ok)


def _best_matching(pred, gold, tools):
    """Pareia chamadas previstas com esperadas maximizando (nome igual + argumentos corretos)."""
    n, m = len(pred), len(gold)
    if n == 0 or m == 0:
        return []
    def score(i, j):
        if pred[i]["name"] != gold[j]["name"]:
            return 0.0
        good, total, ok = _args_result(pred[i], gold[j], tools.get(gold[j]["name"]))
        return 1.0 + (good / total if total else 1.0) + (1.0 if ok else 0.0)
    if max(n, m) <= 6:
        best, best_s = [], -1.0
        k = min(n, m)
        for js in itertools.permutations(range(m), k):
            for is_ in itertools.combinations(range(n), k):
                sc = sum(score(i, j) for i, j in zip(is_, js))
                if sc > best_s:
                    best, best_s = list(zip(is_, js)), sc
        return [(i, j) for i, j in best if score(i, j) > 0]
    used, pairs = set(), []
    for j in range(m):
        cands = [(score(i, j), i) for i in range(n) if i not in used and score(i, j) > 0]
        if cands:
            _, i = max(cands)
            used.add(i); pairs.append((i, j))
    return pairs


def evaluate_decision(raw_output, example):
    """Correcao de um exemplo da trilha de decisao. Retorna dict de metricas por exemplo."""
    tools = {t["name"]: t for t in example["tools"]}
    gold = example.get("gold_calls", [])
    pred, fmt = parse_calls(raw_output)
    if pred is not None:
        try:
            json.dumps(pred, allow_nan=False)
        except (TypeError, ValueError):
            pred, fmt = None, "invalid_json_value"
    res = {"pred_calls": pred, "format": fmt, "format_ok": pred is not None, "gold_is_no_call": len(gold) == 0}
    if pred is None:
        res.update(schema_ok=False, name_ok=False, args_ok=False, exact=False, n_arg_correct=0,
                   n_arg_total=sum(len(g["arguments"]) for g in gold),
                   lenient_no_call=(len(gold) == 0 and not looks_like_call(raw_output) and bool(strip_reasoning(raw_output))),
                   schema_errors=["nao_interpretavel"])
        return res
    errs = [e for c in pred for e in schema_errors(c, tools)]
    res["schema_ok"] = not errs
    res["schema_errors"] = errs
    res["lenient_no_call"] = len(gold) == 0 and len(pred) == 0
    if not gold:
        ok = len(pred) == 0
        res.update(name_ok=ok, args_ok=ok, exact=ok, n_arg_correct=0, n_arg_total=0,
                   false_call=len(pred) > 0)
        return res
    names_ok = sorted(c["name"] for c in pred) == sorted(g["name"] for g in gold)
    pairs = _best_matching(pred, gold, tools)
    n_good = n_tot = 0
    all_args = len(pairs) == len(gold)
    for i, j in pairs:
        good, total, ok = _args_result(pred[i], gold[j], tools.get(gold[j]["name"]))
        n_good += good; n_tot += total
        all_args = all_args and ok
    n_tot += sum(len(gold[j]["arguments"]) for j in range(len(gold)) if j not in {j for _, j in pairs})
    res.update(name_ok=names_ok, args_ok=bool(names_ok and all_args), n_arg_correct=n_good, n_arg_total=n_tot,
               missed_call=len(pred) == 0)
    res["exact"] = bool(res["name_ok"] and res["args_ok"] and len(pred) == len(gold))
    return res
