"""Prompts versionados. Qualquer mudanca de texto exige nova PROMPT_VERSION (registrada no manifest)."""
import json

PROMPT_VERSION = "v1"

def mcq_messages(rec, variant="cot"):
    letters = sorted(rec["choices"])
    opts = "\n".join(f"{l}) {rec['choices'][l]}" for l in letters)
    if variant == "direct":
        instr = "Responda a questao de multipla escolha abaixo. Responda somente no formato 'Resposta: X', sem explicacao."
    else:
        instr = ("Responda a questao de multipla escolha abaixo. Pode raciocinar antes, mas termine "
                 "com uma linha no formato 'Resposta: X', onde X e a letra da alternativa correta.")
    return [{"role": "user", "content": f"{instr}\n\nQuestao: {rec['question']}\n\n{opts}"}]

def decision_messages(rec):
    tools = json.dumps(rec["tools"], ensure_ascii=False, indent=2)
    system = ("Voce tem acesso as ferramentas abaixo (JSON). Escolha a(s) chamada(s) adequada(s) ao pedido do usuario. "
              'Responda SOMENTE com JSON no formato {"calls": [{"name": "...", "arguments": {...}}]}. '
              'Se nenhuma ferramenta for adequada ou faltar informacao obrigatoria, responda {"calls": []}.\n\n'
              f"Ferramentas:\n{tools}")
    return [{"role": "system", "content": system}, {"role": "user", "content": rec["query"]}]
