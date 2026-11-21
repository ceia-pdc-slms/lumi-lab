# Configurações

Versionar configurações de avaliação, inferência e treinamento, separadas dos resultados. Fixar revisões dos modelos, dados e código; registrar alterações relevantes de prompts e parâmetros.

[`run.example.json`](run.example.json) é um modelo de procedência com campos nulos, não uma configuração executável nem evidência de execução. Copie e preencha os campos quando o pipeline estiver implementado; justifique os não aplicáveis. Nunca coloque tokens de acesso nas configurações.

[`benchmark.dummy.json`](benchmark.dummy.json) é o perfil executável sem modelo.
[`benchmark.openai.example.json`](benchmark.openai.example.json) descreve um perfil de inferência com servidor local. Preencha a revisão, quantização, runtime e hardware conforme o [guia](../benchmark/README.md).

[`lumibench-ollama.json`](lumibench-ollama.json) e os [Modelfiles](ollama/) fixam os artefatos do [baseline direct](../benchmark/ollama.md).
