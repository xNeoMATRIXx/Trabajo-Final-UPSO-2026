"""API HTTP de prueba, independiente de Flask y MySQL. Contrato no oficial."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

SOURCE = Path(__file__).resolve().parent / "data/catalogo_prueba.json"


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        resource = urlsplit(self.path).path
        if resource not in {"/lenguajes", "/tecnologias"}:
            return self.respond(404, {"error": "not_found"})
        try:
            data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
            self.respond(200, data[resource.lstrip("/")])
        except (OSError, ValueError, KeyError, TypeError):
            self.respond(503, {"error": "mock_no_disponible"})

    def do_POST(self):
        self.respond(405, {"error": "method_not_allowed"})

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Catalogo HTTP de PRUEBA: http://127.0.0.1:{args.port}", flush=True)
    print("Contrato provisional. Ctrl+C para detener.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
