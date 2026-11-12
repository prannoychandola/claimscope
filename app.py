from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from retrieval import BM25Retriever

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data" / "demo_corpus.json").read_text(encoding="utf-8-sig"))
DOCS = DATA["documents"]
DOC_BY_ID = {str(doc["id"]): doc for doc in DOCS}
DEMO_RETRIEVER = BM25Retriever([
    (doc["id"], " ".join([doc["title"], doc["section"], doc["text"]]))
    for doc in DOCS
])
STATIC = {
    "/": ("static/index.html", "text/html; charset=utf-8"),
    "/app.js": ("static/app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("static/styles.css", "text/css; charset=utf-8"),
}


def rank_evidence(claim: str, top_k: int = 5) -> list[dict]:
    """Return lexical retrieval candidates. A score is not a support verdict."""
    results = []
    for hit in DEMO_RETRIEVER.search(claim, top_k):
        item = dict(DOC_BY_ID[hit.doc_id])
        item["retrieval_score"] = round(hit.score, 4)
        item["query_term_coverage"] = round(hit.query_term_coverage, 4)
        results.append(item)
    return results


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        # Avoid writing user-entered claims to the terminal log.
        return

    def send_bytes(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_bytes(status, "application/json; charset=utf-8", body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self.send_json(
                200,
                {"status": "ok", "documents": len(DOCS), "mode": "fictional demo corpus"},
            )
            return
        asset = STATIC.get(path)
        if asset is None:
            self.send_json(404, {"error": "Not found"})
            return
        relative_path, content_type = asset
        self.send_bytes(200, content_type, (ROOT / relative_path).read_bytes())

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/search":
            self.send_json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Invalid request"})
            return
        if length <= 0 or length > 16_384:
            self.send_json(413, {"error": "Request must be between 1 byte and 16 KB"})
            return
        try:
            request = json.loads(self.rfile.read(length).decode("utf-8"))
            claim = request.get("claim", "")
            if not isinstance(claim, str) or len(claim) > 2_000:
                raise ValueError("Claim must be text up to 2,000 characters")
            candidates = rank_evidence(claim.strip(), request.get("top_k", 5))
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, ValueError, TypeError):
            self.send_json(400, {"error": "Send JSON with a text claim and optional top_k"})
            return
        self.send_json(
            200,
            {
                "claim": claim.strip(),
                "candidates": candidates,
                "notice": "BM25 retrieval candidates only. Relevance is not evidence of support.",
            },
        )


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("ClaimScope is running at http://127.0.0.1:8000")
    print("Local demo only. Claims are not saved or sent to a remote service.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ClaimScope.")
    finally:
        server.server_close()
