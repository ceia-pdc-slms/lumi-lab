"""Inferência com respostas fixas ou com um servidor OpenAI-compatible."""

import json
import os
import time
import urllib.request


class DummyBackend:
    """Exercita o pipeline local sem carregar pesos."""

    def generate(self, messages, *, choice_letters=None, **generation):
        text = '{"calls": []}' if choice_letters is None else "Resposta: A"
        return {"text": text, "n_gen_tokens": None, "latency_s": None}

    def info(self):
        return {"backend": "dummy"}


class OpenAICompatBackend:
    def __init__(self, base_url, model, api_key_env="LUMI_BENCHMARK_API_KEY", timeout=300):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.key = os.environ.get(api_key_env)

    def request_body(self, messages, *, max_new_tokens, temperature, seed):
        return {"model": self.model, "messages": messages, "max_tokens": max_new_tokens,
                "temperature": temperature, "seed": seed}

    def generate(self, messages, *, max_new_tokens, temperature, seed, choice_letters=None):
        body = self.request_body(
            messages, max_new_tokens=max_new_tokens, temperature=temperature, seed=seed,
        )
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        request = urllib.request.Request(
            self.base_url + "/chat/completions", data=json.dumps(body).encode("utf-8"), headers=headers,
        )
        started = time.perf_counter()
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            data = json.load(response)
        choice = data["choices"][0]
        message = choice["message"]
        return {"text": message.get("content") or "", "tool_calls": message.get("tool_calls"),
                "reasoning_output": message.get("reasoning_content") or message.get("reasoning") or message.get("thinking"),
                "finish_reason": choice.get("finish_reason"),
                "n_gen_tokens": (data.get("usage") or {}).get("completion_tokens"),
                "latency_s": time.perf_counter() - started}

    def info(self):
        return {"backend": "openai_compat", "base_url": self.base_url, "model": self.model,
                "timeout_s": self.timeout}


def make_backend(config):
    if config["type"] == "dummy":
        return DummyBackend()
    return OpenAICompatBackend(**{key: value for key, value in config.items() if key != "type"})
