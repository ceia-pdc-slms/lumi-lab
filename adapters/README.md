# Adaptadores de modelos

[`backends.py`](backends.py) fornece respostas fixas para verificação e conecta modelos servidos em uma API OpenAI-compatible. [`outputs.py`](outputs.py) adapta o texto para o avaliador e preserva as chamadas estruturadas fornecidas pelo servidor. O adaptador recebe apenas a saída do modelo.

O adaptador padrão remove marcadores de controle. Na trilha de conhecimento, o adaptador `reasoning` usa a resposta depois do último marcador de resposta final. Na trilha de decisão, a saída segue para o parser comum. As regras e denominadores são os mesmos para os modelos com itens comparáveis.

Veja o [guia do benchmark](../benchmark/README.md) para configurar o servidor e registrar as revisões.
