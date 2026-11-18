# Integração do LumiBench

A integração usa o recorte corrigido do LumiBench como referência de avaliação do Lumi Lab. O primeiro passo é congelar a composição e conferir a origem. O segundo é executar e recalcular a avaliação pelo mesmo código. O terceiro é auditar candidatos de treino contra os dois splits de avaliação.

| Origem no LumiBench | Destino no Lumi Lab |
|---|---|
| `data/benchmark/` e `entrega_semana1/build_manifest.json` | `data/lumibench-v1.json` fixa a revisão, os cinco arquivos canônicos, os hashes e as contagens. O importador instala o snapshot em `data/raw/`. |
| `lumi_bench/` e `schemas/` | `benchmark/` reúne prompts, parsing, pontuação e relatórios. `adapters/` concentra as interfaces de inferência e de saída dos modelos. |
| Configs de execução e `runs/` | `configs/` oferece um perfil sem modelo e um para servidor local. `results/local/` guarda manifest, predições, pontuação e métricas por execução. |
| Ingestão, auditoria e correções de seleção | As revisões dos artefatos upstream ficam referenciadas. A instalação do recorte usa os arquivos finais congelados. |
| Exemplos de integração | O notebook chama a mesma CLI usada no terminal. |

## Etapas de implementação

1. Validar a importação pelo ZIP da revisão exata, testar alteração de conteúdo e conferir as contagens dos cinco conjuntos. Registrar a relação dos hashes LF e CRLF.
2. Usar os parsers e as métricas do LumiBench, gravar saída bruta e normalizada e recalcular a partir das predições com o denominador derivado do manifesto.
3. Auditar treino com IDs, grupos, texto e ferramentas reservadas. Exercitar a CLI, as duas trilhas no notebook e a reprodução offline.

## Decisões e evidência

- **Seleção e divisão.** A unidade de integração é a revisão [`09fbaed`](https://github.com/henriqueelj/Lumi-Benchmark/tree/09fbaed9bfb3c82e3e3d47a70051dbaddaa73c1f). Os 1.000 itens preservam IDs, grupos, setores, gabaritos e splits, inclusive as sete substituições de MATH-PT. A igualdade de 200 itens vale para o recorte completo de cada fonte. A divisão desigual entre desenvolvimento e teste vem da preservação de grupos.
- **Integridade.** Os JSONL do Git usam LF. Os hashes do [registro histórico](https://github.com/henriqueelj/Lumi-Benchmark/blob/09fbaed9bfb3c82e3e3d47a70051dbaddaa73c1f/entrega_semana1/build_manifest.json) coincidem ao representar exatamente as mesmas linhas em CRLF. O importador aceita ambas as representações fixadas e grava LF.
- **Auditoria.** A comparação entre `dev` e `test` encontrou zero pares com Jaccard ≥ 0,8, zero grupos compartilhados e zero nomes de ferramenta em comum. A mesma heurística encontrou três pares dentro de `dev` e três dentro de `test`. Os itens permanecem no recorte original.
- **BFCL.** As perguntas são traduzidas para pt-PT. O upstream registrou 36 itens com 61 argumentos em inglês ausentes do enunciado traduzido. A implementação preserva os gabaritos e as equivalências originais. Qualquer ampliação de equivalências precisa de uma nova revisão de pontuação, aplicada a todos os modelos da comparação.
- **Proveniência.** O catálogo indica o que foi levantado pelo upstream. Confirme as licenças e os termos das fontes antes de redistribuir os arquivos. O projeto também precisa confirmar a licença do código trazido do repositório privado antes de publicar a integração.
- **Treino.** O caminho implementado aceita e audita candidatos separados. Seleção, licenças e geração do corpus de treino continuam pendentes.
- **Reprodução da curadoria.** O uso do benchmark reproduz o snapshot congelado. Para regenerar a seleção a partir das fontes originais, consulte o [recorte efetivo](https://github.com/henriqueelj/Lumi-Benchmark/blob/09fbaed9bfb3c82e3e3d47a70051dbaddaa73c1f/entrega_semana1/recorte.final.json) e as [correções](https://github.com/henriqueelj/Lumi-Benchmark/blob/09fbaed9bfb3c82e3e3d47a70051dbaddaa73c1f/entrega_semana1/relatorio_correcoes.md). Os scripts antigos de `--build` repõem os recortes anteriores às correções e ficam vinculados como histórico.

## Validação local

```bash
python3 -m unittest discover -s tests
python3 -m benchmark validate
```

A verificação inclui o fluxo com backend de respostas fixas nos dois splits, pontuação offline dos 200 gabaritos de BFCL e igualdade entre as métricas originais e recalculadas. A comparação oficial entre checkpoints exige as execuções completas com revisões de dados, modelos e pontuação alinhadas.
