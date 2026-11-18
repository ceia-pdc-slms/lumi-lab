# Contrato comum de avaliação

**Contrato `lumi-lab-lumibench-v1` · prompts `v1` · transporte OpenAI-compatible.** Esta é a especificação de referência do Lumi Lab. A [verificação em desenvolvimento](#verificação-com-o-lumi) registra o que o checkpoint realmente devolveu. A comparação oficial usa os mesmos itens, versões de prompt e regras de pontuação entre os checkpoints comparáveis.

## Mensagens e transporte

Cada item vai em um `POST /v1/chat/completions`, com `model`, `messages`, `max_tokens`, `temperature` e `seed`. O catálogo de ferramentas é texto dentro de `messages`. A requisição v1 omite `tools`, `tool_choice`, `response_format` e controles de *thinking*. O gabarito, os metadados de curadoria e a procedência ficam no avaliador. Veja o [backend](../adapters/backends.py) e os [schemas de dados e predições](../benchmark/schemas/).

### Conhecimento

Uma mensagem `user` leva a instrução, uma linha em branco, `Questao: {question}`, outra linha em branco e as alternativas `A) …`, `B) …` em ordem de letra. A única mensagem enviada ao modelo nessa trilha é `user`. Estas são as instruções literais do [código de prompts](../benchmark/prompts.py).

```text
direct
Responda a questao de multipla escolha abaixo. Responda somente no formato 'Resposta: X', sem explicacao.

cot
Responda a questao de multipla escolha abaixo. Pode raciocinar antes, mas termine com uma linha no formato 'Resposta: X', onde X e a letra da alternativa correta.
```

A saída canônica é `Resposta: B`, com uma letra presente nas opções do item. O avaliador preserva o texto bruto e extrai a letra com o [parser de conhecimento](../benchmark/extract.py).

### Decisão sobre ferramentas

A primeira mensagem é `system` e a segunda é `user`, cujo conteúdo é `query` na íntegra. O prompt é o mesmo com `direct` e `cot`. O texto literal de `system` está abaixo. O único trecho variável é `{tools_json}`, serializado em JSON indentado com dois espaços e preservando Unicode. Cada ferramenta tem `name`, `description` e `parameters`, com as propriedades e os argumentos obrigatórios do item.

```text
Voce tem acesso as ferramentas abaixo (JSON). Escolha a(s) chamada(s) adequada(s) ao pedido do usuario. Responda SOMENTE com JSON no formato {"calls": [{"name": "...", "arguments": {...}}]}. Se nenhuma ferramenta for adequada ou faltar informacao obrigatoria, responda {"calls": []}.

Ferramentas:
{tools_json}
```

Exemplo sintético de ferramenta no `system` e mensagem do usuário.

```json
[{"name":"consultar_pedido","description":"Consulta o status de um pedido.","parameters":{"type":"object","properties":{"numero":{"type":"integer"}},"required":["numero"]}}]
```

```json
{"role":"user","content":"Qual é a situação dos pedidos 42 e 43?"}
```

| Caso | Conteúdo esperado em `assistant` |
|---|---|
| Uma chamada | `{"calls":[{"name":"consultar_pedido","arguments":{"numero":42}}]}` |
| Abstenção | `{"calls":[]}` |
| Múltiplas chamadas | `{"calls":[{"name":"consultar_pedido","arguments":{"numero":42}},{"name":"consultar_pedido","arguments":{"numero":43}}]}` |

O contrato pede um objeto JSON completo, com uma lista `calls` e uma entrada por ação. O avaliador compara nomes e argumentos com o gabarito, preservando a multiplicidade e aceitando qualquer ordem. A abstenção pede a lista explicitamente vazia. O adaptador também registra e interpreta `message.tool_calls` quando o retorno do servidor usa esse campo. A [pontuação](../benchmark/README.md#pontuação) registra separadamente validade do formato, validade dos argumentos e acerto das chamadas. As ferramentas são avaliadas sem execução.

## Chat template e geração do Lumi local

O checkpoint de referência deste ensaio é `lumi:0.2`, GGUF Q4_K_M, no Ollama 0.40.16. O SHA-256 do GGUF, que inclui o tokenizer, é `704dc11770c3a5b0bdd913abbd37cf9821e1b6328d355e1f3021b9f248c32b1a`. O SHA-256 do template Jinja retornado pelo Ollama em `/api/show` é `c2bae541dabb83fe11bf6468864c8d2ad754858c11ee5495b9583c5246567e9f`. Nesse retorno o campo de sistema padrão está vazio. O `system` de decisão vem do avaliador.

Para decisão v1, a estrutura do template é a seguinte. Os marcadores são inseridos pelo runtime e ficam fora do texto das mensagens HTTP.

```text
<|im_start|>system
{system_com_catalogo}
<|im_end|>
<|im_start|>user
{query}<|im_end|>
<|im_start|>assistant
{prefixo_de_raciocinio}
```

O template cria um bloco inicial de sistema vazio caso a primeira mensagem seja `user`. O template declara `enable_thinking=True` por padrão, com prefixo `<think>` na geração. Se esse valor for desativado no template, o prefixo é `<think></think>`. O perfil `direct` controla a instrução da trilha Conhecimento. A política deste ensaio para raciocínio é o padrão do runtime. A captura de `/api/show` é a evidência do template e das condições de parada declaradas, e a captura de requisições registra as mensagens antes da renderização do servidor.

O ensaio usa temperatura `0.0`, seed `42` e até `1024` tokens de saída por item. O modelo anuncia paradas em `<|im_start|>`, `<|im_end|>`, `<think>` e `<|im_start|>user`. O avaliador guarda o motivo de parada e o raciocínio quando o servidor o retorna em um campo separado.

Para treinar o **Lumi Decision** com esse contrato, a receita precisa versionar o texto fixo de `system`, a serialização do catálogo, o turno `user`, a saída-alvo `assistant` e o template e política de raciocínio usados no treino e na inferência. Um protocolo com chamadas nativas tem uma entrada diferente e deve receber um perfil identificável. Use exemplos de treino separados dos itens de `dev` e `test` deste benchmark.

## Verificação com o Lumi

A verificação seleciona de `dev` o primeiro ID em ordem lexicográfica de cada combinação de tarefa e número de chamadas esperadas. O conjunto de três itens é fixado antes de observar as respostas.

```bash
python3 -m benchmark.contract_check \
  --config configs/benchmark.lumi-ollama.contract.json \
  --out results/local/contrato-lumi-dev-repeticao
```

O comando usa o [mesmo backend, prompts e pontuação do benchmark](../benchmark/README.md). A pasta de saída guarda requisições JSON, gabaritos em arquivo separado, predições brutas e normalizadas, pontuação por item, manifesto e métricas. Para outro servidor, preencha o [perfil de inferência](../configs/benchmark.openai.example.json) com as revisões e condições reais.


| Caso em `dev` | ID | Chamadas esperadas e obtidas | Tokens de saída reportados | Resultado |
|---|---|---:|---:|---|
| Uma chamada | `bfcl_pt-multiple_101` | 1 / 1 | 203 | JSON válido, ferramenta e argumentos corretos |
| Abstenção | `bfcl_pt-irrelevance_1` | 0 / 0 | 212 | JSON válido com lista vazia |
| Múltiplas chamadas | `bfcl_pt-parallel_11` | 2 / 2 | 226 | JSON válido, chamadas e argumentos corretos |

O servidor devolveu o motivo de parada `stop` e um campo separado de raciocínio nos três itens. A evidência local está em `results/local/contrato-lumi-dev/`. Ela inclui `runtime.json` com o template reportado pelo servidor e `renderizacao-offline.jsonl` com a renderização Jinja de cada entrada para inspeção. Essa renderização foi produzida fora do servidor com os defaults do template. Os três itens verificam o contrato de decisão. A medição de desempenho usa o split de teste completo em outra execução.
