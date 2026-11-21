# Dados e curadoria

O [catálogo](catalogo-fontes.csv) aponta as cinco fontes e revisões do LumiBench. O [manifesto do recorte](lumibench-v1.json) fixa os arquivos, os SHA-256 e as contagens por split. Obtenha os dados e o avaliador fixado com `python3 -m benchmark.baseline prepare`. Consulte o [guia de execução](../benchmark/ollama.md) para uso com checkout local e reprodução offline.

| Dataset | Desenvolvimento | Teste | Total |
|---|---:|---:|---:|
| OAB Exams | 64 | 136 | 200 |
| DrBodeBench · INEP | 64 | 136 | 200 |
| BLUEX | 65 | 135 | 200 |
| MATH-PT · múltipla escolha | 60 | 140 | 200 |
| BFCL pt-PT | 60 | 140 | 200 |
| **Total** | **313** | **687** | **1.000** |

## Candidatos de treino

No recorte original, `dev` serve para desenvolvimento, validação e calibração. `test` é reservado para a avaliação. A versão importada tem zero itens de treino.

Prepare treino em uma fonte ou recorte separado com procedência, licença e revisão registradas. Forneça os candidatos em JSONL com `split: "train"` e os [campos canônicos](../benchmark/schemas/). Preserve a identidade da origem e dos grupos no campo `dataset` e em `group_id` ao aproveitar itens dos mesmos datasets.

```bash
mkdir -p results/local
python3 -m benchmark audit-train --candidates data/raw/candidatos.jsonl > results/local/auditoria-treino.json
```

A auditoria compara com todo `dev` e `test`, registrando IDs e grupos compartilhados no recorte ou na fonte original, Jaccard de 5-gramas ≥ 0,8 e ferramentas de nome exato reservadas ao teste. Sai com código 1 se houver colisão e 2 se a entrada for inválida. Use o relatório para revisão humana de duplicatas e procedência. A heurística textual tem alcance limitado para traduções, paráfrases e grupos com nomes diferentes.

`raw/` é uma área de trabalho local. A publicação dos dados requer confirmação das licenças e registro da revisão no [índice do Hugging Face](../docs/huggingface.md).
