# Planejamento Lumi — entregas de 12, 19 e 26 de novembro de 2026

A entrega conjunta será um **benchmark implementado e resultados comparativos entre o Lumi original, o Lumi Decision e o Lumi Reasoning**. O trabalho será distribuído em três semanas: planejamento em 12/11, implementação inicial em 19/11 e consolidação e comparação final em 26/11.

## 1. Time de dados e benchmark

### Objetivo e motivação

Construir uma avaliação em português para entender o desempenho do Lumi em diferentes setores e medir o efeito das adaptações realizadas pelo time de fine-tuning.

O benchmark será composto por **dataset de avaliação, regras de correção e código que executa os modelos e calcula os resultados**. Teremos duas trilhas, com resultados apresentados separadamente:

- **Conhecimento por setor:** questões objetivas de áreas como jurídico, saúde, financeiro e agronegócio. Essa trilha mede o desempenho nessas questões; isoladamente, não demonstra capacidade de tomar decisões operacionais.
- **Decisão e comportamento agêntico:** casos de escolha de ações, seleção de ferramentas e preenchimento de argumentos. Nesta primeira versão, avaliaremos a chamada produzida pelo modelo, sem executar as ferramentas. Isso mede decisões sobre ferramentas, mas ainda não o sucesso de um agente em uma tarefa completa.

### Entrega de 12/11 — Especificação e curadoria inicial

Entregar **um documento de especificação, um catálogo de fontes e exemplos preenchidos das duas trilhas**.

O documento deverá resolver os seis requisitos:

1. **Taxonomia:** definir os setores, capacidades e tarefas do recorte inicial, identificando exatamente o que será implementado até 19/11.
2. **Formato dos dados e regras de avaliação:** especificar os campos de entrada, o gabarito e as regras para interpretar e corrigir a resposta. Nos casos agênticos, incluir ferramentas disponíveis, argumentos esperados e chamadas válidas.
3. **Curadoria verificável:** registrar fonte, versão, licença, idioma, revisões, duplicatas e transformações. Distinguir dados originalmente brasileiros de dados traduzidos.
4. **Generalização:** definir treino, desenvolvimento/calibração e teste. Indicar quais categorias, setores ou ferramentas ficarão reservados para avaliar generalização, preservando grupos de exemplos relacionados.
5. **Métricas:** definir fórmulas, agregação e tratamento de falhas. Incluir acerto, validade da resposta e, nos casos agênticos, correção da ferramenta e dos argumentos. Especificar calibração e erro versus cobertura quando houver probabilidades comparáveis.
6. **Execução reproduzível:** definir como carregar os dados, executar os modelos, registrar predições e gerar relatórios, com configurações e versões identificadas.

O **catálogo de fontes**, em planilha ou CSV, deverá mapear datasets públicos candidatos para avaliação e treinamento, indicando a seleção inicial, adaptações necessárias, quantidades e uso previsto. A avaliação terá o mesmo número de exemplos por dataset selecionado; a quantidade será definida pelo time conforme a viabilidade.

Os dois times deverão combinar o que o modelo recebe, qual decisão deve retornar e como será corrigido. Modelos poderão produzir respostas de formas diferentes, desde que um adaptador converta a saída para o formato comum de avaliação. Questões objetivas terão comparação com o gabarito após extração e normalização; chamadas de ferramentas terão comparação dos campos e argumentos definidos.

### Entrega de 19/11 — Benchmark executável e resultados de referência

Entregar:

- **Dataset versionado**, com o recorte aprovado implementado, fontes rastreáveis e separação entre treino, desenvolvimento e teste.
- **Código e notebook executado**, cobrindo as duas trilhas e permitindo reproduzir a avaliação.
- **Arquivo de predições e relatório inicial**, com a execução de um modelo aberto pequeno, como Qwen2.5-0.5B-Instruct, e do Lumi original. Esses resultados serão a referência para avaliar as adaptações na semana seguinte.

O relatório deverá apresentar resultados por dataset, setor e tarefa, além de falhas de resposta, latência e consumo de recursos. Hardware, quantização, prompts e parâmetros de inferência deverão ser registrados. Comparações de velocidade deverão usar condições equivalentes ou deixar explícitas as diferenças.

### Entrega de 26/11 — Comparação final das variantes

Entregar:

- **Execuções do Lumi Decision e do Lumi Reasoning** no mesmo conjunto de teste utilizado para as referências, nas tarefas compatíveis.
- **Relatório comparativo consolidado**, reunindo o modelo aberto de referência, o Lumi original e as duas variantes, com resultados por dataset, setor e tarefa, análise de erros, latência e consumo de recursos.
- **Versão final do pacote do benchmark**, com dados, código, configurações, predições e instruções de reprodução atualizados.

Nesta semana, o foco será integrar as variantes, verificar falhas do avaliador e analisar os resultados. A composição do teste e as regras de pontuação deverão estar fixadas antes da comparação; eventuais correções serão versionadas e aplicadas igualmente a todos os modelos.

## 2. Time de fine-tuning e adaptação

### Objetivo e motivação

Investigar como adaptar o Lumi para **retornar decisões diretamente** e como realizar um **primeiro fine-tuning para reasoning**. Queremos medir o efeito dessas mudanças na qualidade das respostas e no custo de execução.

Para esta etapa:

- **Lumi Decision:** recebe uma tarefa e retorna diretamente uma opção ou ação válida, sem gerar uma explicação intermediária. A exploração deverá verificar quais mecanismos permitem esse comportamento e quais tarefas cada mecanismo suporta.
- **Lumi Reasoning:** recebe fine-tuning com exemplos de resolução intermediária e resposta final. A avaliação verificará se esse treinamento melhora os resultados e qual seu custo; produzir explicações mais longas, por si só, não será considerado ganho.

### Entrega de 12/11 — Plano de adaptação e apresentação técnica

Entregar:

- **Documento de planejamento**, com a pesquisa de pelo menos duas abordagens distintas para adaptar o Lumi à tomada de decisão rápida. Descrever como funcionam, modificações necessárias, tarefas compatíveis, recursos, vantagens e limitações. As abordagens deverão diferir no mecanismo de obtenção da decisão; apenas reformular o mesmo prompt não caracteriza duas adaptações.
- **Plano de implementação para 19 e 26/11**, indicando como executar o Lumi, prototipar e comparar as abordagens, selecionar a adaptação e integrá-la ao benchmark.
- **Plano do primeiro fine-tuning para reasoning**, com fontes de dados em português, formato dos exemplos, estratégia de treinamento e recursos necessários.
- **Apresentação curta para todo o time**, explicando o que são modelos de decisão, como adaptar um LLM para decisões rápidas, quais abordagens serão exploradas e como serão implementadas e avaliadas no Lumi.

A apresentação deverá estar diretamente ligada ao plano de implementação, de modo que o time compreenda as decisões técnicas e os próximos passos. **Nesta primeira semana, a entrega é de pesquisa, planejamento e apresentação; não serão exigidos protótipos nem treinamento executado.**

**Coordenação:** gostaria de pedir que o Gabriel Palhares coordenasse essa pesquisa e a apresentação junto com a Jolie e o Mateus, considerando seu interesse no tema e que essa adaptação de um SLM não fez parte do nivelamento.

### Entrega de 19/11 — Protótipos de decisão e preparação do fine-tuning

Entregar:

- **Notebook de inferência executado**, com o Lumi funcionando, identificação do checkpoint, ambiente, configurações e exemplos de respostas.
- **Código ou notebooks com protótipos de pelo menos duas abordagens de decisão**, executados nos mesmos exemplos de desenvolvimento, registrando decisões, falhas e tempo de execução.
- **Comparação inicial e escolha da abordagem a consolidar**, fundamentada nos resultados e nas limitações observadas.
- **Pipeline inicial de fine-tuning para reasoning**, com dados de treino preparados, configuração e uma execução curta de treinamento para verificar o funcionamento no ambiente escolhido.

Os protótipos deverão utilizar o formato de entrada e saída acordado com o time de benchmark. A comparação inicial usará exemplos de desenvolvimento, preservando o teste para a avaliação final.

### Entrega de 26/11 — Duas variantes experimentais disponíveis para avaliação

Entregar:

- **Lumi Decision**, consolidando a abordagem selecionada e identificando as tarefas suportadas.
- **Lumi Reasoning**, com o primeiro fine-tuning concluído.
- **Código e notebooks de adaptação, treinamento e inferência**, acompanhados de pesos ou adaptadores, configurações e instruções de execução.
- **Integração das variantes com o avaliador**, em conjunto com o time de benchmark, incluindo os adaptadores de saída necessários. As versões deverão ser disponibilizadas durante a semana, com antecedência para executar a comparação até a reunião de 26/11.

As entregas são **versões experimentais**. O compromisso é implementar, executar e comparar; não é obrigatório superar o Lumi original. Uma adaptação sem ganho também produz um resultado válido, desde que os resultados e as limitações sejam registrados.

A comparação deverá avaliar a qualidade da resposta final e registrar também tempo e quantidade de tokens gerados. Nas tarefas que uma variante não suportar, essa limitação deverá aparecer explicitamente no relatório.

### Integração entre as frentes

O formato mínimo de entrada e saída e os exemplos compartilhados deverão ser alinhados na primeira semana, até 12/11, para orientar a implementação dos protótipos na segunda semana. O time de dados disponibilizará progressivamente os dados de treino e desenvolvimento. O teste ficará reservado para a avaliação final, sem ser utilizado para escolher prompts, ajustar métodos ou treinar as variantes.
