from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("PORTFOLIO_DATA_DIR", ROOT / "analytics" / "data"))
DB_PATH = DATA_DIR / "visitors.sqlite3"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))
ALLOWED_ORIGINS = {
    item.strip().rstrip("/")
    for item in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if item.strip()
}


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_views (
                view_date TEXT PRIMARY KEY,
                total_views INTEGER NOT NULL DEFAULT 0
            )
            """
        )


class PortfolioHandler(SimpleHTTPRequestHandler):
    server_version = "PortfolioAnalytics"
    sys_version = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        # Do not write request lines or client addresses to application logs.
        return

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self' https:; base-uri 'self'; "
            "form-action 'none'; frame-ancestors 'none'",
        )
        super().end_headers()

    def translate_path(self, path: str) -> str:
        requested = Path(urlsplit(path).path)
        parts = requested.parts
        if ".git" in parts or (len(parts) >= 3 and parts[:2] == ("analytics", "data")):
            return str(ROOT / "__not_found__")
        if any(part.startswith(".") for part in parts if part not in (".", "..")):
            return str(ROOT / "__not_found__")
        return super().translate_path(path)

    def _origin_allowed(self, origin: str | None) -> bool:
        if not origin:
            return True
        normalized = origin.rstrip("/")
        if normalized in ALLOWED_ORIGINS:
            return True
        parsed = urlsplit(normalized)
        forwarded_scheme = self.headers.get("X-Forwarded-Proto", "http").split(",")[0].strip()
        request_host = self.headers.get("Host", "").lower()
        return parsed.scheme == forwarded_scheme and parsed.netloc.lower() == request_host

    def _add_cors_headers(self) -> None:
        origin = self.headers.get("Origin")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin.rstrip("/"))
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:
        if self.path.split("?", 1)[0] != "/api/visit":
            self.send_error(404)
            return
        origin = self.headers.get("Origin")
        if not self._origin_allowed(origin):
            self.send_error(403)
            return
        self.send_response(204)
        self._add_cors_headers()
        self.end_headers()

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/api/visit":
            self.send_error(404)
            return

        origin = self.headers.get("Origin")
        if not self._origin_allowed(origin):
            self.send_error(403)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if not 0 < length <= 128:
            self.send_error(413)
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400)
            return
        if payload != {"event": "page_view"}:
            self.send_error(400)
            return

        view_date = datetime.now(timezone.utc).date().isoformat()
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """
                INSERT INTO daily_views (view_date, total_views)
                VALUES (?, 1)
                ON CONFLICT(view_date) DO UPDATE
                SET total_views = total_views + 1
                """,
                (view_date,),
            )

        response = json.dumps({"ok": True}, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self._add_cors_headers()
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    initialize_database()
    server = ThreadingHTTPServer((HOST, PORT), PortfolioHandler)
    print(f"Portfolio local: http://{HOST}:{PORT}/")
    print("Métricas agregadas em analytics/data/visitors.sqlite3")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
