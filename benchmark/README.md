# LumiBench no Lumi Lab

Use Python 3.10+ na raiz do Lumi Lab. O avaliador usa a biblioteca padrão. O modo de demonstração roda também no [notebook](../notebooks/lumibench.ipynb).

## Instalar e conferir o recorte

Baixe o ZIP da [revisão fixada do LumiBench](https://github.com/henriqueelj/Lumi-Benchmark/tree/09fbaed9bfb3c82e3e3d47a70051dbaddaa73c1f) com a sua conta do projeto ou use um checkout dessa revisão. A importação usa os cinco JSONL canônicos, confere os hashes e verifica IDs, gabaritos, contagens, grupos, sobreposição de texto entre splits e nomes de ferramentas. O recorte fica em `data/raw/lumibench-v1/`; todos os comandos aceitam `--data-dir` para escolher outro local.

```bash
python3 -m benchmark import --source /caminho/para/Lumi-Benchmark-09fbaed9bfb3c82e3e3d47a70051dbaddaa73c1f.zip
python3 -m benchmark validate
```

## Executar e recalcular

```bash
# Demonstração autocontida com quatro exemplos sintéticos
python3 -m benchmark run --suite demo --out results/local/demo

# Recorte completo de desenvolvimento ou teste, com respostas fixas
python3 -m benchmark run --split dev --out results/local/dummy-dev
python3 -m benchmark run --split test --out results/local/dummy-test

# Recorte pequeno de desenvolvimento para verificar um servidor local
mkdir -p results/local
cp configs/benchmark.openai.example.json results/local/modelo.json
# Preencha o ID do modelo servido, os hashes das revisões e o ambiente do servidor
python3 -m benchmark run --config results/local/modelo.json --split dev \
  --dataset math_pt --dataset bfcl_pt --limit-per-dataset 1 --out results/local/modelo-dev

# Recálculo offline com a mesma revisão do avaliador e dos dados
python3 -m benchmark score --run results/local/modelo-dev --out results/local/modelo-dev-replay
```

O perfil de inferência usa `/v1/chat/completions` de um servidor compatível, por exemplo Ollama, llama.cpp ou vLLM. Use commit ou SHA-256 para pesos e tokenizer. Num GGUF com tokenizer incorporado, use o hash do próprio GGUF nos dois campos. Registre runtime, hardware, quantização e, quando aplicável, template e tamanho de contexto do servidor em `model`. A chave opcional vem da variável `LUMI_BENCHMARK_API_KEY`.

`prompt_variant` aceita `direct` ou `cot` na trilha A. O prompt da trilha B é o mesmo para as duas variantes. O envio contém apenas enunciado e alternativas ou pedido e ferramentas disponíveis. Respostas fixas exercitam a integração. A avaliação com modelo usa o perfil de inferência. O limite por dataset é permitido em `dev`; no teste, cada dataset escolhido é executado inteiro. O manifesto indica se o recorte é parcial.

O [contrato de avaliação](../docs/contrato-avaliacao.md) fixa as mensagens, o formato de decisão, o template do Lumi e o comando de verificação dos três casos em desenvolvimento.

Cada execução grava `config.json`, `manifest.json`, predições brutas e normalizadas, pontuação por item, métricas JSON e relatório Markdown. O manifesto fixa hashes, IDs na ordem de execução, revisão do avaliador e parâmetros. O recálculo usa os IDs do manifesto como denominador e sinaliza predições alteradas ou ausentes em `replay.json`. Use um diretório de saída novo a cada execução.

## Pontuação

| Trilha | Resultado principal | Diagnósticos |
|---|---|---|
| A · Conhecimento | Alternativas corretas / todos os itens selecionados | Validade, acurácia nas válidas, IC Wilson de 95% |
| B · Decisão | Chamadas equivalentes ao gabarito / todos os itens selecionados | Formato, schema, nomes, argumentos e abstenção |

Em B, o parser interpreta a saída e compara chamadas sem executá-las. O pareamento preserva a multiplicidade e ignora a ordem das chamadas. As equivalências do LumiBench incluem tolerância numérica, normalização de caixa e acentos, valores alternativos explicitados no gabarito e parâmetros extras com o valor padrão. O parser rejeita blocos com chamadas malformadas e ignora raciocínio incompleto. A validade de schema verifica nomes, campos obrigatórios, tipos e enumerações no primeiro nível dos argumentos. Por exemplo, um número recebido em texto pode ser semanticamente equivalente e ter tipo inválido no schema.

A taxa por argumento usa o total de argumentos esperados nos itens com chamada, com a regra upstream de argumentos opcionais. Abstenção usa itens sem chamada esperada. Uma resposta explícita com lista vazia em um caso que pede ferramenta conta como chamada omitida. Respostas inválidas, timeouts e predições ausentes contam como erro no resultado principal. Cobertura é a fração com registro de predição, incluindo registros de falha. Métricas sem denominador aparecem como `null`. O JSON detalha dataset, setor e tarefa dentro de cada trilha. Calibração fica pendente de uma fonte de probabilidades comparáveis por alternativa.

Veja as [decisões de migração](../docs/integracao-lumibench.md) e os [critérios para treino](../data/README.md).

## Múltipla escolha em uma passada

O backend opcional `choice_logits` usa o mesmo enunciado e as alternativas do perfil `direct`. Renderiza o template com `enable_thinking=False`, inclui `Resposta:` no lado do assistente e escolhe a letra de maior logit. O registro da predição inclui os logits das alternativas válidas, os IDs desses tokens e o tamanho da entrada em tokens. O manifesto registra a configuração, o hash do template e o hash do executável. Veja a [compilação e o perfil](../adapters/native/README.md).

Para comparar em desenvolvimento, rode os dois perfis sobre os mesmos itens, com os quatro datasets de conhecimento e o mesmo limite por dataset:

```bash
python3 -m benchmark run --split dev --config /caminho/para/o/perfil.json \
  --dataset oab_exams --dataset drbodebench_inep --dataset bluex --dataset math_pt \
  --limit-per-dataset 3 --out results/local/perfil-dev
```
