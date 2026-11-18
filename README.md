# Lumi Lab

Repositório público das frentes de **dados e benchmark** e **adaptação e fine-tuning** do grupo de Lucca no CEIA/UFG. Desenvolvemos e comparamos o Lumi original, o Lumi Decision e o Lumi Reasoning com dados em português e execuções reproduzíveis.

O [guia do benchmark](benchmark/README.md) mostra como validar o recorte do LumiBench, executar as duas trilhas e recalcular as métricas. O [mapa de integração](docs/integracao-lumibench.md) registra a origem dos dados e as decisões pendentes.

## Comece aqui

1. Leia as [entregas de novembro](docs/entregas.md) e o [planejamento completo](docs/planejamento/entregas-novembro-2026.md).
2. Consulte as [tarefas e dependências](docs/tarefas.md) e escolha uma issue da sua frente.
3. Combine a responsabilidade individual na issue e siga o [guia de contribuição](CONTRIBUTING.md).
4. Feche o [contrato de avaliação](docs/contrato-avaliacao.md) com a outra frente antes de integrar implementações.

## O que vamos comparar

| Trilha | O que mede | Limite desta etapa |
|---|---|---|
| Conhecimento por setor | Respostas objetivas em datasets de setores selecionados | Não comprova tomada de decisão operacional |
| Decisão sobre ferramentas | Escolha da ferramenta/ação, validade da resposta e argumentos | Avalia a chamada produzida; não executa ferramentas nem mede sucesso agêntico completo |

Os resultados são separados por trilha, dataset, setor e tarefa. Uma variante pode suportar somente parte das tarefas: a cobertura precisa aparecer no relatório. O compromisso é implementar, executar e comparar; superar o Lumi original não é requisito.

## Entregas

| Marco | Dados e benchmark | Adaptação e fine-tuning |
|---|---|---|
| **19/11/2026** | Dataset versionado; avaliador e notebook das duas trilhas; predições e relatório do modelo pequeno e Lumi original | Lumi funcionando; pelo menos dois mecanismos de decisão comparados em desenvolvimento; pipeline de reasoning com treino curto executado |
| **26/11/2026** | Avaliação das variantes no mesmo teste; análise comparativa; pacote reproduzível | Lumi Decision consolidado; primeiro fine-tuning de reasoning concluído; integração e artefatos disponibilizados |

Versões candidatas devem chegar à integração **até 24/11**, como meta operacional para permitir avaliação antes de 26/11. Veja o [acompanhamento](docs/entregas.md).

## Onde cada coisa fica

| Local | Conteúdo |
|---|---|
| [`benchmark/`](benchmark/README.md) | Carregamento, execução, pontuação e relatórios do benchmark |
| [`adaptation/`](adaptation/README.md) | Protótipos de decisão e treinamento para reasoning |
| [`adapters/`](adapters/README.md) | Integração das saídas dos modelos com o formato comum |
| [`configs/`](configs/README.md) | Configurações e modelos de registro de execução |
| [`data/`](data/README.md) | Catálogo de fontes, curadoria e referências para dados versionados |
| [`notebooks/`](notebooks/README.md) | Demonstrações e notebooks executados das entregas |
| [`results/`](results/README.md) | Predições, resumos, erros e referências dos experimentos |
| [`docs/`](docs/README.md) | Planejamento, contrato, metodologia e decisões |

O avaliador roda com Python e biblioteca padrão. O servidor de inferência roda à parte e sua versão, seu hardware e a revisão dos pesos e do tokenizer ficam no manifesto da execução.

## Público e reproduzível

- Código, datasets, resultados e modelos serão públicos. Pesos abertos e datasets serão disponibilizados no Hugging Face; os IDs definitivos entram no [registro de publicação](docs/huggingface.md).
- O teste pode ser público e deve permanecer fixado e reservado metodologicamente à avaliação: não usá-lo para treino, escolha de prompts ou seleção de abordagens.
- Toda execução identifica código, checkpoint/revisão do modelo, versão dos dados, prompts, parâmetros, hardware e quantização. Consulte a [metodologia](docs/experimentos.md).
- Binários de modelos e grandes volumes de dados ficam no Hugging Face; aqui entram seus identificadores, revisões e instruções de reprodução.

## Equipes

| Frente | Integrantes |
|---|---|
| Dados e benchmark | Ana Clara, Elisa e Henrique |
| Adaptação e fine-tuning | Gabriel Palhares, Jolie e Mateus |
| Coordenação e integração | Lucca |

A coordenação da pesquisa de decisão é de Gabriel Palhares, conforme o planejamento. As atribuições individuais das demais tarefas são combinadas nas issues.

## Conexões com o projeto

- [Fase 1 — acervo de nivelamento](https://github.com/ceia-pdc-slms/fase-1-nivelamento).
- [Hub público do PDC](https://ceia-pdc-slms.github.io/): receberá a página Lumi e os resultados desta etapa.
- [Código do hub](https://github.com/ceia-pdc-slms/ceia-pdc-slms.github.io): a publicação da página está organizada como tarefa, ainda não executada.

Este repo é a continuidade experimental do grupo. O planejamento de novembro orienta esta entrega; materiais anteriores sobre seleção de papers continuam como contexto histórico.
