#!/usr/bin/env python3
import argparse
import os
import posixpath
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
RELOAD_PATH = "/__live_reload"
IGNORED_DIRS = {".git", ".idea", "__pycache__"}
WATCH_EXTENSIONS = {
    ".css",
    ".html",
    ".jpeg",
    ".jpg",
    ".js",
    ".json",
    ".png",
    ".svg",
    ".webp",
}

LIVE_RELOAD_SNIPPET = """
<script>
(() => {
  const source = new EventSource('/__live_reload');
  source.addEventListener('reload', () => window.location.reload());
})();
</script>
"""


def latest_mtime():
    latest = 0.0
    for directory, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
        for filename in filenames:
            path = Path(directory) / filename
            if path.suffix.lower() not in WATCH_EXTENSIONS:
                continue
            try:
                latest = max(latest, path.stat().st_mtime)
            except OSError:
                continue
    return latest


class LiveReloadHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        if urlparse(self.path).path == RELOAD_PATH:
            self.stream_reload_events()
            return
        super().do_GET()

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            for index in ("index.html", "index.htm"):
                index_path = os.path.join(path, index)
                if os.path.exists(index_path):
                    path = index_path
                    break

        if Path(path).suffix.lower() != ".html":
            return super().send_head()

        try:
            content = Path(path).read_text(encoding="utf-8")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        if "</body>" in content:
            content = content.replace("</body>", f"{LIVE_RELOAD_SNIPPET}</body>", 1)
        else:
            content += LIVE_RELOAD_SNIPPET

        encoded = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return MemoryFile(encoded)

    def translate_path(self, path):
        path = urlparse(path).path
        path = posixpath.normpath(unquote(path))
        parts = [part for part in path.split("/") if part and part not in (os.curdir, os.pardir)]
        resolved = ROOT
        for part in parts:
            resolved /= part
        return str(resolved)

    def stream_reload_events(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        last_seen = latest_mtime()
        try:
            while True:
                current = latest_mtime()
                if current > last_seen:
                    last_seen = current
                    self.wfile.write(b"event: reload\ndata: changed\n\n")
                    self.wfile.flush()
                else:
                    self.wfile.write(b": keep-alive\n\n")
                    self.wfile.flush()
                time.sleep(0.7)
        except (BrokenPipeError, ConnectionResetError):
            return


class MemoryFile:
    def __init__(self, content):
        self.content = content

    def read(self, _size=-1):
        content, self.content = self.content, b""
        return content

    def close(self):
        return None


def main():
    parser = argparse.ArgumentParser(description="Static dev server with live reload.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8010, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), LiveReloadHandler)
    print(f"Serving {ROOT} at http://{args.host}:{args.port}/ with live reload")
    server.serve_forever()


if __name__ == "__main__":
    main()
