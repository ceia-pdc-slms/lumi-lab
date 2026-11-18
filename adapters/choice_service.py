"""Endpoint local de múltipla escolha com um único processo de logits."""

import argparse
from contextlib import ExitStack
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import re
import signal
import time
import uuid

from .choice_logits import ChoiceLogitsBackend

HOST = "127.0.0.1"
PROTOCOL = "choice_logits_v1"
MAX_REQUEST_BYTES = 1_000_000


def port_for(endpoint):
    match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})", endpoint)
    if not match or int(match[1]) > 65535:
        raise ValueError("Use um endpoint local no formato http://127.0.0.1:PORTA")
    return int(match[1])


def parse_request(payload):
    if not isinstance(payload, dict) or set(payload) != {"messages", "choice_letters"}:
        raise ValueError("Esperava messages e choice_letters")
    messages, letters = payload["messages"], payload["choice_letters"]
    if (not isinstance(messages, list) or len(messages) != 1 or not isinstance(messages[0], dict)
            or set(messages[0]) != {"role", "content"} or messages[0]["role"] != "user"
            or not isinstance(messages[0]["content"], str) or not messages[0]["content"].strip()):
        raise ValueError("Esperava uma mensagem user de múltipla escolha")
    if not isinstance(letters, str) or len(letters) < 2 or not re.fullmatch(r"[A-J]+", letters) or (
        len(set(letters)) != len(letters)
    ):
        raise ValueError("Esperava letras distintas entre A e J")
    return messages, letters


def require_model(expected, actual):
    for key in ("revision", "tokenizer_revision", "chat_template_sha256"):
        if expected[key] != actual.get(key):
            raise ValueError(f"Endpoint usa uma revisão diferente em model.{key}")


class ChoiceEndpointBackend:
    def __init__(self, endpoint, model):
        self.port = port_for(endpoint)
        status = self.request("GET", "/health")
        if status["protocol"] != PROTOCOL or status["backend"]["thinking"] is not False:
            raise ValueError("Endpoint incompatível com logits em uma passada")
        require_model(model, status["model"])
        self.instance = status["instance"]
        self.metadata = {**status["backend"], "backend": "choice_logits_http", "endpoint": endpoint,
                         "instance": self.instance, "load_s": status["load_s"]}

    def request(self, method, path, payload=None):
        connection = HTTPConnection(HOST, self.port, timeout=125)
        try:
            connection.request(method, path, body=json.dumps(payload) if payload is not None else None,
                               headers={"Content-Type": "application/json"} if payload is not None else {})
            response = connection.getresponse()
            result = json.load(response)
            if response.status != 200:
                raise RuntimeError(f"Endpoint de logits retornou HTTP {response.status}")
            return result
        finally:
            connection.close()

    def generate(self, messages, *, choice_letters, **generation):
        started = time.perf_counter()
        body = self.request("POST", "/predict", {"messages": messages, "choice_letters": choice_letters})
        if body["instance"] != self.instance:
            raise RuntimeError("O endpoint de logits reiniciou durante a execução")
        row = body["prediction"]
        return {**row, "server_latency_s": row["latency_s"], "latency_s": time.perf_counter() - started}

    def info(self):
        return self.metadata


class Handler(BaseHTTPRequestHandler):
    timeout = 10

    def reply(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def check_host(self):
        if self.headers.get("Host") == f"{HOST}:{self.server.server_port}":
            return True
        self.reply(400, {"error": "host"})
        return False

    def do_GET(self):
        if not self.check_host():
            return
        if self.path != "/health":
            self.reply(404, {"error": "route"})
        elif self.server.backend.process.poll() is not None:
            self.reply(503, {"error": "worker_unavailable"})
        else:
            self.reply(200, {**self.server.metadata, "completed_requests": self.server.completed_requests})

    def do_POST(self):
        if not self.check_host():
            return
        if self.path != "/predict":
            self.reply(404, {"error": "route"})
            return
        if self.headers.get_content_type() != "application/json":
            self.reply(415, {"error": "content_type"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_REQUEST_BYTES:
                raise ValueError("Tamanho inválido")
            messages, letters = parse_request(json.loads(self.rfile.read(size)))
        except (ValueError, TimeoutError):
            self.reply(400, {"error": "invalid_request"})
            return
        try:
            result = self.server.backend.generate(messages, choice_letters=letters)
        except ValueError:
            self.reply(422, {"error": "invalid_choices_or_prompt"})
            return
        except (RuntimeError, OSError):
            self.reply(503, {"error": "worker_unavailable"})
            return
        self.server.completed_requests += 1
        self.reply(200, {"instance": self.server.metadata["instance"], "prediction": result})


def main():
    from benchmark.run import configuration

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="perfil de execução choice_logits")
    parser.add_argument("--port", type=int, default=11440)
    args = parser.parse_args()
    config, _, _ = configuration(args.config)
    if config["backend"]["type"] != "choice_logits" or not 1 <= args.port <= 65535:
        parser.error("Informe um perfil local choice_logits e uma porta válida")

    def stop(_signum, _frame):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    with HTTPServer((HOST, args.port), Handler) as server, ExitStack() as resources:
        started = time.perf_counter()
        backend = ChoiceLogitsBackend(config["backend"], config["model"])
        resources.callback(backend.close)
        server.backend = backend
        server.completed_requests = 0
        server.metadata = {
            "protocol": PROTOCOL, "instance": uuid.uuid4().hex, "backend": backend.info(),
            "model": config["model"], "worker_pid": backend.process.pid,
            "load_s": time.perf_counter() - started,
        }
        print(f"Lumi pronto em http://{HOST}:{args.port} ({server.metadata['load_s']:.2f} s de inicialização).", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
