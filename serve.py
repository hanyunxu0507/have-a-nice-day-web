from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
(ROOT / "port.txt").write_text(str(server.server_address[1]), encoding="utf-8")
server.serve_forever()
