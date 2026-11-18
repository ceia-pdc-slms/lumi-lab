# Avaliador GGUF de múltipla escolha

O processo local recebe o prompt já renderizado e as letras válidas do item. Ele tokeniza o prompt e verifica, no contexto de resposta, que acrescentar cada letra após `Resposta:` acrescenta um único token distinto, mantendo o restante da entrada. Em seguida, faz uma chamada a `llama_decode` para obter os logits da última posição e devolve apenas os das alternativas. A decisão usa o maior desses logits. O processo não gera tokens e limpa o estado entre itens.

## Compilação no macOS

Use a revisão de [llama.cpp `6c01da627`](https://github.com/ggml-org/llama.cpp/tree/6c01da627), correspondente à base do runner do Ollama no ensaio. Com o checkout em `/caminho/llama.cpp`, compile com as ferramentas de linha de comando da Apple e CMake.

```bash
LLAMA_CHOICE_SRC=/caminho/llama.cpp
LLAMA_CHOICE_BUILD="$PWD/results/local/llama-build"
LLAMA_CHOICE_SDK="$(xcrun --show-sdk-path)"
cmake -S "$LLAMA_CHOICE_SRC" -B "$LLAMA_CHOICE_BUILD" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_SYSROOT="$LLAMA_CHOICE_SDK" \
  -DCMAKE_CXX_FLAGS="-isystem $LLAMA_CHOICE_SDK/usr/include/c++/v1" \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_TOOLS=OFF \
  -DGGML_METAL=ON -DGGML_METAL_EMBED_LIBRARY=ON
cmake --build "$LLAMA_CHOICE_BUILD" --target llama --parallel 8
clang++ -std=c++17 -O2 -isysroot "$LLAMA_CHOICE_SDK" \
  -isystem "$LLAMA_CHOICE_SDK/usr/include/c++/v1" \
  -I"$LLAMA_CHOICE_SRC/include" -I"$LLAMA_CHOICE_SRC/ggml/include" \
  adapters/native/llama_choice.cpp -L"$LLAMA_CHOICE_BUILD/bin" \
  -Wl,-rpath,"$LLAMA_CHOICE_BUILD/bin" -lllama -lggml \
  -o "$LLAMA_CHOICE_BUILD/llama_choice"
```

O backend Python usa Jinja2 para renderizar o template. Para repetir as condições do ensaio, instale `Jinja2==3.1.6` no ambiente do benchmark. Exporte o campo `template` de `/api/show` do checkpoint local como UTF-8, preservando seus bytes e o SHA-256. Use um perfil de execução no formato abaixo, com os caminhos absolutos adequados e as demais propriedades de `model` copiadas do perfil do checkpoint.

```json
{
  "backend": {
    "type": "choice_logits",
    "executable": "/caminho/llama_choice",
    "weights": "/caminho/Lumi.gguf",
    "template": "/caminho/chat_template.jinja",
    "context_size": 4096
  },
  "model": {
    "revision": "<SHA-256 do GGUF>",
    "tokenizer_revision": "<Mesmo SHA-256 do GGUF>",
    "chat_template_sha256": "<SHA-256 do template>",
    "quantization": "Q4_K_M",
    "runtime": "llama.cpp@6c01da627 (Metal)",
    "hardware": "Apple M3 Pro"
  },
  "prompt_variant": "direct"
}
```
