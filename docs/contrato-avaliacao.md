# Contrato comum de avaliação

**Estado da revisão pelas duas frentes.** A implementação candidata do LumiBench está descrita no [guia de execução e pontuação](../benchmark/README.md). Os [schemas](../benchmark/schemas/) documentam seus arquivos JSONL. A aprovação formal do contrato continua na tarefa de integração.

## Entrada de cada exemplo

Combinar nomes, tipos e exemplos preenchidos para:

- ID estável; dataset e revisão; setor; trilha; tarefa; split e grupo de exemplos relacionados.
- Texto de entrada, alternativas e identificadores válidos nas questões objetivas.
- Ferramentas disponíveis, descrição, schema dos argumentos e ações válidas nos casos de decisão.
- Gabarito separado da entrada enviada ao modelo, incluindo as equivalências aceitas.
- Proveniência: fonte, licença, idioma original e transformações.

## Saída de cada adaptador

Combinar uma representação normalizada da alternativa ou chamada escolhida, preservando também a resposta bruta. Registrar ferramenta e argumentos, validade, falha de parsing, timeout e outras falhas sem descartar o exemplo.

Modelos podem retornar formatos diferentes. O adaptador faz a conversão para o formato comum; não altera o gabarito para favorecer um modelo. Não executar as ferramentas nesta versão.

## Regras de pontuação

Definir extração e normalização, equivalência dos argumentos, tratamento de múltiplas chamadas e resposta inválida. Especificar fórmulas, denominadores, agregação por dataset/setor/tarefa e cobertura das variantes.

Calibração e erro versus cobertura só entram quando houver probabilidades comparáveis. Registrar como essas probabilidades são obtidas; não tratar texto de autoconfiança como probabilidade calibrada.

## Evidência mínima para fechar o contrato

- Exemplos preenchidos das duas trilhas, incluindo casos válidos e inválidos.
- Revisão de ambas as frentes, com decisão registrada na issue/PR.
- Revisão identificada do contrato antes das execuções de referência.
- Mudanças posteriores versionadas e aplicadas igualmente aos modelos afetados.
