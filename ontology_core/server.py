"""HTTP server for the local ontology study hub."""

from __future__ import annotations

import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

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
from .learner_model import (
    append_event,
    evaluate_beliefs,
    explain_belief,
    load_events,
    load_profile,
    recommend_next,
    save_profile,
)
from .notes import load_doc_sections
from .paths import ARTIFACTS_DIR, ROOT, WEB_DIR

MIME_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".mjs": "application/javascript; charset=utf-8",
    ".md": "text/plain; charset=utf-8",
    ".pdf": "application/pdf",
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

    def _file_range(self, path: Path) -> None:
        try:
            resolved = path.resolve()
            if not resolved.is_relative_to(ROOT):
                raise FileNotFoundError
            file_size = resolved.stat().st_size
            range_header = self.headers.get("Range")
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return

        content_type = MIME_TYPES.get(resolved.suffix, "application/octet-stream")
        if not range_header:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self._cors()
            self.end_headers()
            if self.command != "HEAD":
                with resolved.open("rb") as handle:
                    self.wfile.write(handle.read())
            return

        match = re.match(r"bytes=(\d*)-(\d*)$", range_header)
        if not match:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self._cors()
            self.end_headers()
            return

        start_s, end_s = match.groups()
        if start_s:
            start = int(start_s)
            end = int(end_s) if end_s else file_size - 1
        else:
            suffix = int(end_s or "0")
            start = max(file_size - suffix, 0)
            end = file_size - 1

        if start >= file_size or end < start:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self._cors()
            self.end_headers()
            return

        end = min(end, file_size - 1)
        length = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Accept-Ranges", "bytes")
        self._cors()
        self.end_headers()
        if self.command == "HEAD":
            return
        with resolved.open("rb") as handle:
            handle.seek(start)
            self.wfile.write(handle.read(length))

    def _body(self) -> dict | list:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        if path == "/":
            self._file(WEB_DIR / "index.html")
        elif path == "/favicon.ico":
            self.send_response(204)
            self._cors()
            self.end_headers()
        elif path.startswith("/web/"):
            self._file(ROOT / path.lstrip("/"))
        elif path.startswith("/lib/"):
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
        elif re.match(r"^/api/docs/[^/]+/pdf$", path):
            doc_id = path.split("/")[3]
            doc = next((item for item in load_documents() if item["id"] == doc_id), None)
            if doc:
                self._file_range(ROOT / doc["source_path"])
            else:
                self._json({"error": "not found"}, 404)
        elif re.match(r"^/api/docs/[^/]+/sections$", path):
            doc_id = path.split("/")[3]
            result = load_doc_sections(doc_id)
            self._json(result if result else {"error": "not found"}, 200 if result else 404)
        elif path == "/api/learner/profile":
            self._json(load_profile())
        elif path == "/api/learner/events":
            raw_limit = query.get("limit", [None])[0]
            try:
                limit = int(raw_limit) if raw_limit is not None else None
            except ValueError:
                limit = None
            concept_id = query.get("concept_id", [None])[0]
            self._json(load_events(limit=limit, concept_id=concept_id))
        elif path == "/api/learner/beliefs":
            self._json(evaluate_beliefs())
        elif re.match(r"^/api/learner/explain/.+$", path):
            belief_id = unquote(path.removeprefix("/api/learner/explain/"))
            result = explain_belief(belief_id)
            self._json(result, 404 if result.get("error") else 200)
        elif path == "/api/learner/recommendations":
            raw_limit = query.get("limit", [8])[0]
            try:
                limit = int(raw_limit)
            except ValueError:
                limit = 8
            self._json(recommend_next(limit=limit))
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
        if path == "/api/learner/profile":
            self._json(save_profile(self._body()))
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
        if path == "/api/learner/events":
            event = append_event(data)
            beliefs = evaluate_beliefs()
            self._json({"event": event, "beliefs": beliefs}, 201)
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
    ThreadingHTTPServer(("localhost", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
