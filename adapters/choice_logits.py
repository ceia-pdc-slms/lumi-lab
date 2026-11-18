"""Inferência de múltipla escolha com leitura dos logits do último token."""

import hashlib
import json
import math
import select
import subprocess
import time
from pathlib import Path


def sha256_file(path):
    with Path(path).open("rb") as handle:
        digest = hashlib.sha256()
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def choose_letter(letters, logits):
    if len(letters) < 2 or len(set(letters)) != len(letters) or not set(letters) <= set("ABCDEFGHIJ"):
        raise ValueError("Alternativas inválidas")
    if set(logits) != set(letters) or any(
        type(value) not in (float, int) or not math.isfinite(value) for value in logits.values()
    ):
        raise ValueError("Esperava um logit finito por alternativa válida")
    return max(letters, key=logits.__getitem__)


class ChoiceLogitsBackend:
    def __init__(self, backend, model):
        from jinja2.sandbox import SandboxedEnvironment

        template = Path(backend["template"]).read_bytes()
        if hashlib.sha256(template).hexdigest() != model["chat_template_sha256"]:
            raise ValueError("SHA-256 do template diferente da configuração")
        if sha256_file(backend["weights"]) != model["revision"]:
            raise ValueError("SHA-256 do GGUF diferente da configuração")
        if model["tokenizer_revision"] != model["revision"]:
            raise ValueError("O tokenizer dessa modalidade é o embutido no GGUF")
        self.template = SandboxedEnvironment().from_string(template.decode("utf-8"))
        self.metadata = {
            "backend": "choice_logits", "thinking": False, "assistant_prefix": "\nResposta:",
            "executable_sha256": sha256_file(backend["executable"]), "context_size": backend["context_size"],
        }
        self.process = subprocess.Popen(
            [backend["executable"], backend["weights"], str(backend["context_size"])],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        )
        try:
            if self._read().get("ready") is not True:
                raise RuntimeError("Falha ao inicializar o avaliador de logits")
        except BaseException:
            self.close()
            raise

    def _read(self):
        if not select.select([self.process.stdout], [], [], 120)[0]:
            raise TimeoutError("Tempo limite do processo de logits")
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError(f"Processo de logits encerrado ({self.process.poll()})")
        return json.loads(line)

    def generate(self, messages, *, choice_letters, **generation):
        if not choice_letters or not set(choice_letters) <= set("ABCDEFGHIJ"):
            raise ValueError("Alternativas inválidas")
        started = time.perf_counter()
        prompt = self.template.render(
            messages=messages, add_generation_prompt=True, enable_thinking=False,
        )
        if not prompt.endswith("<think></think>"):
            raise ValueError("O template não confirmou o prefixo de thinking desabilitado")
        encoded = (prompt + self.metadata["assistant_prefix"]).encode("utf-8")
        pipe = self.process.stdin
        pipe.write(f"{len(encoded)} {choice_letters}\n".encode("ascii"))
        pipe.write(encoded)
        pipe.flush()
        try:
            response = self._read()
        except TimeoutError:
            self.process.kill()
            raise
        if response.get("error"):
            raise ValueError(f"Falha na decisão em uma passada: {response['error']}")
        logits = response["logits"]
        return {
            "text": choose_letter(choice_letters, logits), "n_gen_tokens": 0,
            "latency_s": time.perf_counter() - started, "finish_reason": "decision",
            "choice_logits": logits, "choice_token_ids": response["token_ids"],
            "prompt_tokens": response["prompt_tokens"],
        }

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        finally:
            self.process.stdout.close()

    def info(self):
        return self.metadata
