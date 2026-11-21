# LumiBench direct no Ollama

Comparação local de 21/11/2026 entre **Lumi-4B v0.2** e **Qwen3-4B-Instruct-2507**. Rodamos os mesmos itens por split com o prompt `direct`, o extrator upstream e thinking desligado. O Lumi usou GGUF Q4_K_XL, identificado como Q4_K_M pelo Ollama, e o Qwen3 usou GGUF Q4_K_M. Ollama 0.40.16, Apple M3 Pro, contexto de 8.192 tokens. [Como reproduzir](../../benchmarks/lumibench/v1/README.md)

## Acertos por base

| Base | Dev · Lumi | Dev · Qwen3 | Teste · Lumi | Teste · Qwen3 |
|---|---:|---:|---:|---:|
| OAB Exams | 22/64 | 31/64 | 66/136 | 62/136 |
| DrBodeBench · INEP | 45/64 | 42/64 | 75/136 | 75/136 |
| BLUEX | 47/65 | 48/65 | 95/135 | 95/135 |
| MATH-PT | 19/60 | 26/60 | 38/140 | 34/140 |
| **Múltipla escolha** | **133/253 · 52,6%** | **147/253 · 58,1%** | **274/547 · 50,1%** | **266/547 · 48,6%** |
| **BFCL · chamada exata** | **48/60 · 80,0%** | **54/60 · 90,0%** | **99/140 · 70,7%** | **113/140 · 80,7%** |

O Lumi teve oito acertos a mais em múltipla escolha no teste. O Qwen3 teve quatorze chamadas exatas a mais no BFCL. O placar reproduz o gabarito congelado. No item `bluex-USP_2021_5` de dev, o dataset marca A, o gabarito oficial marca D e a resposta D do Lumi foi pontuada como erro. [Questão e gabarito oficial](https://acervo.fuvest.br/fuvest/2021/fuvest_2021_analise_1_fase_grupos.pdf)

## Latência HTTP por item

| Split e trilha | Lumi · mediana / p95 | Qwen3 · mediana / p95 |
|---|---:|---:|
| Dev · múltipla escolha | 1,31 s / 2,54 s | 0,67 s / 1,29 s |
| Dev · BFCL | 2,68 s / 5,68 s | 1,67 s / 4,14 s |
| Teste · múltipla escolha | 1,13 s / 2,36 s | 0,73 s / 1,37 s |
| Teste · BFCL | 2,84 s / 6,53 s | 1,92 s / 5,46 s |

Os tempos vêm de rodadas sequenciais no mesmo Mac. A rodada completa de teste levou 19 min 05 s no Lumi e 12 min 28 s no Qwen3. Os quatro ensaios terminaram sem falhas de inferência.

## Evidências

| Split | Resumo recalculado | Rodada Lumi | Rodada Qwen3 |
|---|---|---|---|
| Dev · 313 itens | [JSON](dev.json) | [Manifesto e predições](lumi-direct-dev/) | [Manifesto e predições](qwen3-4b-direct-dev/) |
| Teste · 687 itens | [JSON](test.json) | [Manifesto e predições](lumi-direct-test/) | [Manifesto e predições](qwen3-4b-direct-test/) |

As predições preservam o texto processado pelo adaptador upstream, a latência, os tokens e a falha por item. O manifesto original mantém o hash da configuração histórica. Os [perfis versionados](../../benchmarks/lumibench/v1/profiles/ollama-direct/models.json) permitem recriar a configuração efetiva. O [guia de reprodução](../../benchmarks/lumibench/v1/README.md#recalcular-os-resultados-registrados) mostra como recalcular os dois placares.
