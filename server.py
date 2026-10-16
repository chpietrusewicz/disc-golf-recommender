import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

import recommender


ROOT = Path(__file__).parent
PUBLIC_DIR = ROOT / "public"


def json_safe_records(frame):
    return json.loads(frame.to_json(orient="records"))


class RequestHandler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        if not path.is_file() or PUBLIC_DIR not in path.parents:
            self.send_error(404)
            return

        content_type = {
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".html": "text/html; charset=utf-8",
        }.get(path.suffix, "application/octet-stream")
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/config":
            brands = sorted(recommender.df["brand"].dropna().unique())
            self.send_json(
                {
                    "brands": brands,
                    "defaultBrands": recommender.RECOMMENDED_BRANDS,
                }
            )
            return

        if route in {"/", "/index.html"}:
            self.send_file(PUBLIC_DIR / "index.html")
            return

        requested = (PUBLIC_DIR / route.lstrip("/")).resolve()
        self.send_file(requested)

    def do_POST(self):
        if urlparse(self.path).path != "/api/recommend":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(content_length))
            query = str(payload.get("query", "")).strip()
            selected_brands = payload.get("brands", [])
            if not query:
                raise ValueError("Enter a description of the disc you want.")
            if not isinstance(selected_brands, list):
                raise ValueError("Brands must be a list.")

            selected = {str(brand).casefold() for brand in selected_brands}
            candidates = recommender.df[
                recommender.df["brand"].fillna("").str.casefold().isin(selected)
            ].copy()
            results = recommender.smart_recommend(query, candidates, top_n=6)
            self.send_json({"results": json_safe_records(results)})
        except (ValueError, json.JSONDecodeError, KeyError, TypeError) as error:
            self.send_json({"error": str(error)}, status=400)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), RequestHandler)
    print("Discwise is running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Discwise.")
    finally:
        server.server_close()
