"""
Local preview server for the blog and the blargl editor.

    python3 serve.py            # http://localhost:8000
    python3 serve.py --port 9000

The editor lives at /blargl/. Saving a post from there writes posts/*.md
and rebuilds the site. The save endpoint only accepts connections from
localhost.
"""

import argparse
import json
import os
import posixpath
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

import publish

ROOT = publish.ROOT
OUT_DIR = publish.OUT_DIR
POSTS_DIR = publish.POSTS_DIR


def filename_from_title(title):
    stem = title.strip().replace(" ", "_")
    stem = stem.replace("/", "").replace("\\", "").replace("\0", "")
    return (stem or "Untitled") + ".md"


def compose_markdown(title, date, body):
    escaped = title.replace("\\", "\\\\").replace('"', '\\"')
    body = body.lstrip("\n")
    return f'---\ntitle: "{escaped}"\ndate: {date}\n---\n\n{body}'


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=OUT_DIR, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _is_local(self):
        host = self.client_address[0]
        return host in ("127.0.0.1", "::1", "localhost")

    def _json(self, code, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = unquote(posixpath.normpath(self.path.split("?", 1)[0]))
        if path != "/api/save":
            self.send_error(404)
            return
        if not self._is_local():
            self._json(403, {"error": "save is only allowed on localhost"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "invalid JSON"})
            return

        title = (payload.get("title") or "").strip()
        date = (payload.get("date") or "").strip()
        body = payload.get("body") or ""
        markdown = payload.get("markdown")
        filename = payload.get("filename")

        if markdown is None:
            if not title:
                self._json(400, {"error": "title is required"})
                return
            if not date:
                self._json(400, {"error": "date is required"})
                return
            markdown = compose_markdown(title, date, body)
            filename = filename_from_title(title)

        filename = os.path.basename(filename or "")
        if not filename.endswith(".md"):
            filename += ".md"
        if filename in (".md",) or filename.startswith("."):
            self._json(400, {"error": "invalid filename"})
            return

        os.makedirs(POSTS_DIR, exist_ok=True)
        dest = os.path.join(POSTS_DIR, filename)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(markdown if markdown.endswith("\n") else markdown + "\n")

        publish.build_all()
        url = "/" + filename[:-3] + ".html"
        self._json(200, {"filename": filename, "url": url, "path": f"posts/{filename}"})


def main():
    parser = argparse.ArgumentParser(description="Preview the blog locally.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    os.chdir(ROOT)
    publish.build_all()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Blog:   http://127.0.0.1:{args.port}/")
    print(f"Editor: http://127.0.0.1:{args.port}/blargl/")
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
