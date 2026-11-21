# Reproduzir o baseline LumiBench no Ollama

O baseline compara Lumi-4B v0.2 e Qwen3-4B-Instruct-2507 em geração `direct`. Use Git, Python 3.10+ e um Ollama local ativo em `127.0.0.1:11434`. As rodadas registradas usaram Ollama 0.40.16 em um Apple M3 Pro. Execute os comandos na raiz do Lumi Lab.

## Obter e validar os dados

```sh
python3 -m benchmark.baseline prepare
```

O comando obtém o [avaliador upstream fixado](https://github.com/henriqueelj/Lumi-Benchmark/tree/27c93a1f70ee4a0ce577d3e6a64b819bbdd87d26) em `.cache/lumi-benchmark/` e instala os cinco JSONL canônicos em `data/raw/lumibench-v1/`. O [manifesto dos dados](../data/lumibench-v1.json) registra os hashes, a origem e os splits. A importação confere 1.000 IDs, **313 em `dev` e 687 em `test`**, e reutiliza os dados locais quando já foram validados. Use `--source /caminho/do/checkout` antes de `prepare`, `run` ou `compare` para indicar uma cópia local da mesma revisão.

O checkout fixado fornece os prompts e as regras de extração e pontuação do experimento. A CLI integrada descrita no [guia geral](README.md) tem seu próprio contrato de parsing.

## Preparar os modelos

```sh
ollama pull hf.co/Mateus-Nery/lumi-4b-GGUF:Q4_K_XL
ollama pull qwen3:4b-instruct-2507-q4_K_M
ollama cp hf.co/Mateus-Nery/lumi-4b-GGUF:Q4_K_XL lumi:0.2
ollama create lumi:0.2-benchmark -f configs/ollama/lumi.Modelfile
ollama create qwen3:4b-instruct-benchmark -f configs/ollama/qwen3.Modelfile
```

Os [perfis](../configs/lumibench-ollama.json) fixam o digest dos aliases, o SHA-256 dos pesos e o hash do chat template. O comando de avaliação confere esses dados e aquece cada modelo antes de medir. O contexto é de 8.192 tokens e o limite de saída é de 512, com temperatura zero, seed 42 e `reasoning_effort=none`. O modelo devolve texto ou JSON em `message.content`. A geração de logits de alternativas e a execução de ferramentas pertencem a outros protocolos.

## Executar e comparar

Para verificar a integração, rode um exemplo de cada trilha em desenvolvimento.

```sh
python3 -m benchmark.baseline run --model lumi --split dev --limit 1 --out results/local/smoke-lumi
ollama stop lumi:0.2-benchmark
python3 -m benchmark.baseline run --model qwen3 --split dev --limit 1 --out results/local/smoke-qwen3
```

Execute o split completo em série para medir latência sem competição entre as rodadas. Troque `test` por `dev` para a rodada de desenvolvimento completa, com nomes de saída próprios.

```sh
python3 -m benchmark.baseline run --model lumi --split test --out results/local/lumi-test
ollama stop lumi:0.2-benchmark
python3 -m benchmark.baseline run --model qwen3 --split test --out results/local/qwen3-test

python3 -m benchmark.baseline compare --split test \
  --lumi results/local/lumi-test --qwen3 results/local/qwen3-test
```

Cada rodada escreve a configuração, o manifesto, as predições, a pontuação e o placar em um diretório novo. `compare` recalcula os acertos a partir das predições e confere os hashes dos cinco arquivos e a cobertura e a ordem dos IDs. A latência é o tempo HTTP por requisição completa no cliente, sem o aquecimento. O resumo inclui mediana e p95 por trilha. Registre o runtime, o hardware, a quantização e as falhas ao interpretar a comparação.

## Recalcular os resultados registrados

Após `prepare`, estes comandos funcionam sem Ollama e sem pesos.

```sh
entry=results/lumibench-direct-ollama
python3 -m benchmark.baseline compare --split test \
  --lumi "$entry/lumi-direct-test" --qwen3 "$entry/qwen3-4b-direct-test"
```

O [registro dos resultados](../results/lumibench-direct-ollama/README.md) aponta também para os artefatos de `dev`.
