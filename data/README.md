# Dados e curadoria

[`catalogo-fontes.csv`](catalogo-fontes.csv) começa somente com o cabeçalho; as fontes ainda precisam ser selecionadas e verificadas pelo time.

Registrar fonte, versão, licença, idioma/origem, revisões, transformações, duplicatas, grupos relacionados, quantidades e uso previsto. A quantidade de avaliação deve ser igual por dataset selecionado, conforme o recorte viável.

Os dados e splits são públicos e serão versionados no Hugging Face. Aqui ficam o catálogo, scripts de preparação, manifests e revisões usadas. Os diretórios `raw/` e `cache/` são locais e ignorados pelo Git, sem restringir a publicação dos dados curados.

Separar treino, desenvolvimento/calibração e teste. Não utilizar o teste para selecionar métodos ou treinar. Veja a [metodologia](../docs/experimentos.md) e as [tarefas](../docs/tarefas.md).
