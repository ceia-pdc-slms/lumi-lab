# Publicação dos artefatos

Código, dados, resultados e pesos são públicos. O GitHub concentra o pipeline e o acompanhamento; Hugging Face concentra os artefatos de modelos e datasets. O hub apresenta resultados revisados e links para as fontes.

## Registro a preencher na tarefa de publicação

| Artefato | Repositório/ID público | Revisão/tag avaliada | Situação inicial |
|---|---|---|---|
| Checkpoint original usado como referência | A registrar | A registrar | Referência a confirmar |
| Lumi Decision | A registrar | A registrar | Variante a consolidar |
| Lumi Reasoning | A registrar | A registrar | Fine-tuning a executar |
| Dataset do benchmark | A registrar | A registrar | Curadoria a concluir |
| Dados de treino para reasoning | A registrar | A registrar | Preparação a concluir |

Não inventar namespace ou URL antes da criação/confirmação. A avaliação deve apontar para a revisão exata, não apenas para uma branch mutável.

## Cada modelo

Publicar os pesos abertos e arquivos necessários à inferência, ou o artefato de adaptação aplicável com instruções completas. Uma variante obtida somente por mecanismo de inferência pode reutilizar os pesos-base: nesse caso, publicar e versionar o mecanismo/configuração, sem apresentar pesos idênticos como um novo fine-tuning.

Incluir modelo-base e revisão, tokenizer/template, dependências, exemplo de uso, tarefas suportadas, dados e receita de treinamento quando houver, resultados e limitações. Registrar a licença aplicável aos artefatos e fontes. Se houver adaptador, indicar como carregá-lo e qual base usar.

## Cada dataset

Publicar card com fontes, versões, licenças, idioma, transformações, taxonomia e splits. Registrar quantidade por dataset e preservação de grupos relacionados. Explicar o uso avaliativo do teste, mesmo sendo público.

## Página Lumi no hub

Criar uma página de acompanhamento no repo do hub, com situação das entregas, modelos, metodologia, resultados das duas trilhas e links de reprodução. As tabelas devem consumir resumos exportados do avaliador e manter as versões identificadas.

A publicação da página é uma tarefa de 26/11; ela pode começar com resultados preliminares de 19/11 claramente identificados. Não executar inferência ou treinamento no build do site.
