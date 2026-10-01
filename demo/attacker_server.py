"""Local-only demonstration collector. Never use with real data."""
from http.server import BaseHTTPRequestHandler, HTTPServer

class Collector(BaseHTTPRequestHandler):
    received = []
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size).decode(errors="replace")
        self.received.append(body)
        print("[ATTACKER DEMO] received:", body)
        self.send_response(204); self.end_headers()
    def log_message(self, *args): pass

if __name__ == "__main__":
    print("Local demo collector listening at http://localhost:9999/collect")
    HTTPServer(("127.0.0.1", 9999), Collector).serve_forever()
