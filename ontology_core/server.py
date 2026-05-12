"""HTTP server for the local ontology study hub."""

from __future__ import annotations

import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .knowledge_base import (
    insert_node,
    load_documents,
    load_nodes,
    load_relations,
    load_schema,
    remove_node,
    save_relations,
    update_node,
)
from .notes import load_doc_sections
from .paths import ARTIFACTS_DIR, ROOT, WEB_DIR

MIME_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".md": "text/plain; charset=utf-8",
    ".yaml": "text/yaml; charset=utf-8",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.command:7} {self.path}")

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, data, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path: Path) -> None:
        try:
            resolved = path.resolve()
            if not resolved.is_relative_to(ROOT):
                raise FileNotFoundError
            data = resolved.read_bytes()
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", MIME_TYPES.get(resolved.suffix, "text/plain; charset=utf-8"))
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict | list:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/":
            self._file(WEB_DIR / "index.html")
        elif path == "/favicon.ico":
            self.send_response(204)
            self._cors()
            self.end_headers()
        elif path.startswith("/web/"):
            self._file(ROOT / path.lstrip("/"))
        elif path.startswith("/artifacts/"):
            self._file(ARTIFACTS_DIR / path.removeprefix("/artifacts/"))
        elif path == "/api/nodes":
            self._json(load_nodes())
        elif path == "/api/relations":
            self._json(load_relations())
        elif path == "/api/schema":
            self._json(load_schema())
        elif path == "/api/docs":
            self._json(load_documents())
        elif re.match(r"^/api/docs/[^/]+/sections$", path):
            doc_id = path.split("/")[3]
            result = load_doc_sections(doc_id)
            self._json(result if result else {"error": "not found"}, 200 if result else 404)
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        match = re.match(r"^/api/nodes/(.+)$", path)
        if match:
            node_id = match.group(1)
            if update_node(node_id, self._body()):
                self._json({"ok": True})
            else:
                self._json({"error": "not found"}, 404)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        data = self._body()
        if path == "/api/nodes":
            error = insert_node(data)
            self._json({"error": error}, 409) if error else self._json({"ok": True})
            return
        if path == "/api/relations":
            relations = load_relations()
            relations.append(data)
            save_relations(relations)
            self._json({"ok": True})
            return
        self.send_response(404)
        self.end_headers()

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        match = re.match(r"^/api/nodes/(.+)$", path)
        if match:
            node_id = match.group(1)
            if remove_node(node_id):
                self._json({"ok": True})
            else:
                self._json({"error": "not found"}, 404)
            return

        if path == "/api/relations":
            data = self._body()
            relations = [
                rel
                for rel in load_relations()
                if not (
                    rel.get("type") == data.get("type")
                    and rel.get("source") == data.get("source")
                    and rel.get("target") == data.get("target")
                )
            ]
            save_relations(relations)
            self._json({"ok": True})
            return

        self.send_response(404)
        self.end_headers()


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    port = int(argv[0]) if argv else 5173
    print(f"\n  Ontology browser -> http://localhost:{port}\n")
    HTTPServer(("localhost", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
