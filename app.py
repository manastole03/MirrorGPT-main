#!/usr/bin/env python3
"""Dependency-free local web UI for the MirrorGPT Lite baseline."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from baseline import answer_question


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
PROFILE_PATH = ROOT / "mirror" / "data" / "sample" / "crosleythomas_linkedin.txt"
MAX_REQUEST_BYTES = 16_384

STATIC_FILES = {
    "/": (WEB_ROOT / "index.html", "text/html; charset=utf-8"),
    "/index.html": (WEB_ROOT / "index.html", "text/html; charset=utf-8"),
    "/styles.css": (WEB_ROOT / "styles.css", "text/css; charset=utf-8"),
    "/app.js": (WEB_ROOT / "app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": (WEB_ROOT / "favicon.svg", "image/svg+xml; charset=utf-8"),
}


def answer_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Enter a question before running the baseline.")
    question = question.strip()
    if len(question) > 500:
        raise ValueError("Question must be 500 characters or fewer.")
    result = answer_question(question, PROFILE_PATH)
    result["profile"] = str(PROFILE_PATH.relative_to(ROOT))
    result["engine"] = "deterministic rule-and-retrieval baseline"
    return result


class MirrorHandler(BaseHTTPRequestHandler):
    server_version = "MirrorGPTLite/1.0"

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")

    def send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict[str, object], status: int = 200) -> None:
        self.send_bytes(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
        )

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self.send_json({"status": "ok", "profile_loaded": PROFILE_PATH.exists()})
            return
        static = STATIC_FILES.get(path)
        if static is None:
            self.send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
            return
        file_path, content_type = static
        try:
            self.send_bytes(file_path.read_bytes(), content_type)
        except FileNotFoundError:
            self.send_json({"error": "UI asset is missing."}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/answer":
            self.send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise ValueError("Invalid request size.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            self.send_json(answer_payload(payload))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json({"error": "Request body must be valid UTF-8 JSON."}, HTTPStatus.BAD_REQUEST)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", default=8765, type=int, help="Port (default: 8765)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), MirrorHandler)
    print(f"MirrorGPT Lite UI: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
