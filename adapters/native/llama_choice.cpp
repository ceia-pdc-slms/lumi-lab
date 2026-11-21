#include "llama.h"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

static std::vector<llama_token> tokenize(const llama_vocab * vocab, const std::string & text) {
    int32_t needed = llama_tokenize(vocab, text.data(), static_cast<int32_t>(text.size()),
                                   nullptr, 0, true, true);
    if (needed >= 0) {
        throw std::runtime_error("tokenization_size");
    }
    std::vector<llama_token> tokens(-needed);
    int32_t count = llama_tokenize(vocab, text.data(), static_cast<int32_t>(text.size()),
                                  tokens.data(), static_cast<int32_t>(tokens.size()), true, true);
    if (count != static_cast<int32_t>(tokens.size())) {
        throw std::runtime_error("tokenization");
    }
    return tokens;
}

static void score(llama_context * context, const llama_vocab * vocab,
                  const std::string & prompt, const std::string & letters) {
    auto tokens = tokenize(vocab, prompt);
    if (tokens.size() >= llama_n_ctx(context)) {
        throw std::runtime_error("context_limit");
    }
    std::vector<llama_token> labels;
    std::set<llama_token> distinct;
    for (char letter : letters) {
        auto extended = tokenize(vocab, prompt + " " + letter);
        if (extended.size() != tokens.size() + 1 ||
                !std::equal(tokens.begin(), tokens.end(), extended.begin()) ||
                !distinct.insert(extended.back()).second) {
            throw std::runtime_error("letter_is_not_a_distinct_single_token");
        }
        labels.push_back(extended.back());
    }

    llama_memory_clear(llama_get_memory(context), true);
    if (llama_decode(context, llama_batch_get_one(tokens.data(), tokens.size())) != 0) {
        throw std::runtime_error("decode");
    }
    const float * logits = llama_get_logits_ith(context, -1);
    if (logits == nullptr) {
        throw std::runtime_error("logits");
    }
    for (auto id : labels) {
        if (!std::isfinite(logits[id])) {
            throw std::runtime_error("nonfinite_logit");
        }
    }
    std::cout << "{\"prompt_tokens\":" << tokens.size() << ",\"logits\":{";
    for (size_t i = 0; i < labels.size(); ++i) {
        if (i) std::cout << ',';
        std::cout << '"' << letters[i] << "\":" << std::setprecision(std::numeric_limits<float>::max_digits10)
                  << logits[labels[i]];
    }
    std::cout << "},\"token_ids\":{";
    for (size_t i = 0; i < labels.size(); ++i) {
        if (i) std::cout << ',';
        std::cout << '"' << letters[i] << "\":" << labels[i];
    }
    std::cout << "}}" << std::endl;
}

int main(int argc, char ** argv) {
    if (argc != 3) {
        std::cerr << "usage: llama_choice MODEL_GGUF CONTEXT_SIZE\n";
        return 2;
    }
    int context_size = std::stoi(argv[2]);
    if (context_size < 4 || context_size > 32768) return 2;

    llama_backend_init();
    ggml_backend_load_all();
    auto model_parameters = llama_model_default_params();
    model_parameters.n_gpu_layers = 999;
    std::unique_ptr<llama_model, decltype(&llama_model_free)> model(
        llama_model_load_from_file(argv[1], model_parameters), llama_model_free);
    if (!model) return 1;

    auto parameters = llama_context_default_params();
    parameters.n_ctx = context_size;
    parameters.n_batch = context_size;
    parameters.n_seq_max = 1;
    std::unique_ptr<llama_context, decltype(&llama_free)> context(
        llama_init_from_model(model.get(), parameters), llama_free);
    if (!context) return 1;
    const auto * vocab = llama_model_get_vocab(model.get());
    std::cout << "{\"ready\":true}" << std::endl;

    size_t length;
    std::string letters;
    while (std::cin >> length >> letters) {
        if (std::cin.get() != '\n' || length > 1'000'000 ||
                letters.size() < 2 || letters.size() > 10 ||
                letters.find_first_not_of("ABCDEFGHIJ") != std::string::npos) return 2;
        std::string prompt(length, '\0');
        if (!std::cin.read(prompt.data(), length)) return 2;
        try {
            score(context.get(), vocab, prompt, letters);
        } catch (const std::exception & error) {
            std::cout << "{\"error\":\"" << error.what() << "\"}" << std::endl;
        }
    }
}
