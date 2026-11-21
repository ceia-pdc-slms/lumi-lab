# Benchmarks do Lumi Lab

| Benchmark | Versão publicada | O que avalia | Resultados |
|---|---|---|---|
| LumiBench | [`lumibench/v1`](lumibench/v1/README.md) | 800 questões de conhecimento e 200 casos de decisão sobre ferramentas | [Lumi e Qwen3 no Ollama](../results/lumibench-direct-ollama/README.md) |

O guia de cada versão reúne dados, protocolo e comandos. Use `python3 -m benchmark --help` na raiz do repo para ver a CLI.

- Uma **versão de dados** fixa itens, splits e gabaritos por hash. Corrigir um gabarito exige identificar a revisão e recalcular os resultados afetados.
- Um **protocolo** fixa a revisão do avaliador, a versão do prompt e a adaptação da resposta. Registre mudanças que possam alterar a pontuação.
- Um **perfil de execução** fixa modelo, quantização, runtime e parâmetros de geração. Cada rodada registra seu ambiente no manifesto.
