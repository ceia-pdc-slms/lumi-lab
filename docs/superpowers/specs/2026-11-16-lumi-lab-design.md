# Lumi Lab — organização inicial

## Intenção e escopo aprovado

Criar `ceia-pdc-slms/lumi-lab` como repositório público compartilhado pelas frentes de dados/benchmark e adaptação/fine-tuning. A organização é a mesma de `fase-1-nivelamento`. A aprovação foi dada na conversa de 16/11/2026, incluindo a criação do repo, estrutura inicial, README, guia de contribuição e tarefas para 19 e 26/11/2026.

O planejamento de novembro é a fonte dos requisitos de pesquisa. Esta preparação organiza o trabalho; não implementa o avaliador, não executa treinamento nem declara entregas científicas concluídas.

## Abordagens consideradas

- Continuar na fase 1: aproveita o endereço, mas mistura acervo didático e pesquisa.
- Um novo repo compartilhado: mantém interfaces, configurações e integração próximas. **Escolhido pelo usuário.**
- Dois novos repos por frente: permite ciclos independentes, mas aumenta a sincronização nesta entrega conjunta.

## Decisões

- GitHub: código, notebooks, configurações, curadoria e relatórios.
- Hugging Face: modelos com pesos abertos, adaptadores quando aplicáveis e datasets públicos.
- Hub `ceia-pdc-slms.github.io`: acompanhamento e resultados publicados.
- Todo o trabalho é público, incluindo os dados. O teste é fixado e reservado metodologicamente à avaliação, sem restrição de acesso inventada.
- As trilhas de conhecimento e decisão sobre ferramentas são apresentadas separadamente. Nesta versão, ferramentas não são executadas.
- A entrega de 19/11 inclui referências do modelo pequeno e Lumi original, dois protótipos de decisão e treino curto de reasoning. A entrega de 26/11 integra e compara as variantes experimentais.
- O repo da fase 1 permanece como acervo. Nenhum conteúdo existente será movido ou alterado.

## Estrutura e fluxo

Pastas por componente: `benchmark/`, `adaptation/`, `adapters/`, `configs/`, `data/`, `notebooks/`, `results/` e `docs/`. Nesta preparação, pastas recebem guias, não implementações fictícias.

Issues terão frente, prioridade, marco, dependências e critérios de aceite. A atribuição individual é feita pelo time na issue; os trios atuais são registrados sem inventar uma nova distribuição de trabalho. O time `pdc-membros`, já usado na fase 1, terá acesso de escrita. Como os seis integrantes são colaboradores diretos e não membros desse time, receberão também convites individuais de escrita, que dependem de aceite. PRs pequenos e revisão por code owners orientam a integração.

## Critérios de conclusão desta preparação

1. Repo público na organização correta, com branch padrão `main` e conteúdo publicado.
2. README e CONTRIBUTING navegáveis, fonte de planejamento preservada e cada pasta explicada.
3. Dois marcos com datas de 19 e 26/11/2026 no fuso de São Paulo.
4. Tarefas abertas cobrindo o planejamento, sem atribuir resultados não realizados.
5. Links, JSON, CSV, configuração do GitHub e estado remoto verificados.

## Fora deste pedido

Executar as tarefas de pesquisa, criar repositórios no Hugging Face, publicar a página no hub e escolher mecanismos de adaptação. Essas atividades ficam organizadas nas issues.
