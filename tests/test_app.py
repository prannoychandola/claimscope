from __future__ import annotations

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import Handler


class AppHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_homepage_and_static_assets_load(self):
        for path, expected in (
            ("/", b"ClaimScope"),
            ("/app.js", b"/api/search"),
            ("/styles.css", b"font-family"),
        ):
            with self.subTest(path=path), urlopen(self.base_url + path) as response:
                self.assertEqual(response.status, 200)
                self.assertIn(expected, response.read())
                self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_health_endpoint_describes_demo_corpus(self):
        with urlopen(self.base_url + "/api/health") as response:
            payload = json.load(response)
        self.assertEqual(payload["status"], "ok")
        self.assertGreater(payload["documents"], 0)
        self.assertEqual(payload["mode"], "fictional demo corpus")

    def test_search_returns_ranked_candidates_and_disclaimer(self):
        body = json.dumps({"claim": "hybrid retrieval evidence recall", "top_k": 3}).encode()
        request = Request(self.base_url + "/api/search", data=body, headers={"Content-Type": "application/json"})
        with urlopen(request) as response:
            payload = json.load(response)
        self.assertTrue(payload["candidates"])
        self.assertLessEqual(len(payload["candidates"]), 3)
        self.assertIn("not evidence of support", payload["notice"])

    def test_search_rejects_invalid_json(self):
        request = Request(self.base_url + "/api/search", data=b"not json", headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as raised:
            urlopen(request)
        self.assertEqual(raised.exception.code, 400)

    def test_unknown_route_returns_not_found(self):
        with self.assertRaises(HTTPError) as raised:
            urlopen(self.base_url + "/missing")
        self.assertEqual(raised.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
