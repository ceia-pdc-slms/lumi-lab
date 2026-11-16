# Metodologia e procedência

## Dados e avaliação

O benchmark contém duas trilhas separadas: conhecimento por setor e decisão sobre ferramentas. Não há execução de ferramentas nesta versão. A taxonomia e o recorte implementável precisam ser registrados no contrato.

O catálogo deve distinguir dados originalmente brasileiros de traduções, registrar revisões e licença, transformações, deduplicação e grupos relacionados. A avaliação usa o mesmo número de exemplos por dataset selecionado, com quantidade definida pelo time conforme a viabilidade.

Os splits são públicos. Treino ajusta os modelos; desenvolvimento orienta seleção de abordagens, prompts e calibração; teste é fixado para avaliação. Reservas de setores, categorias ou ferramentas precisam preservar grupos relacionados e ser documentadas como teste de generalização. A publicidade do teste não torna a avaliação cega nem elimina possível contaminação prévia.

## Identifique cada execução

Registre pelo menos:

- ID e data da execução; responsável; commit do código e estado de alterações locais.
- Modelo/checkpoint e revisão exata, modelo-base, adaptador e tokenizer/template usados.
- Dataset, revisão, split, IDs dos exemplos e versão do avaliador.
- Prompt/template, seed, parâmetros e limites de inferência.
- Hardware, sistema, runtime/bibliotecas, precisão/quantização e tamanho de contexto.
- Tempos, memória, quantidade de tokens e falhas; unidade e método de medição.
- Caminhos/URLs das configurações, predições brutas/normalizadas, métricas e logs úteis.

[`configs/run.example.json`](../configs/run.example.json) é um modelo de registro, não uma execução. Campos nulos precisam ser preenchidos ou justificados como não aplicáveis.

## Compare com clareza

Apresente resultados por trilha, dataset, setor e tarefa. Separe qualidade final, validade, acerto da ferramenta e dos argumentos. Mostre quantidade de exemplos, falhas e cobertura; tarefas incompatíveis devem estar explícitas.

Não remova respostas inválidas ou timeouts para melhorar a acurácia. Fixe as regras antes da comparação e documente eventuais correções, reavaliando todos os modelos afetados.

Compare velocidade sob condições equivalentes ou deixe as diferenças explícitas. Registre o orçamento de geração e a quantidade de tokens: produzir mais raciocínio não é, isoladamente, ganho. Se uma abordagem não gera tokens, registre essa condição sem inventar uma medida equivalente.

Resultados sem ganho são válidos quando o experimento, a evidência e as limitações estão documentados.
