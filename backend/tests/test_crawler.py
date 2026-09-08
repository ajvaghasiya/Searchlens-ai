import os
import sys
import threading
import http.server

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.crawler import crawl_page
from app.services.scoring import score_page

GOOD_HTML = """
<html>
<head>
  <title>A Perfectly Reasonable Page Title Under Sixty Chars</title>
  <meta name="description" content="A meta description that is long enough to pass the seventy character minimum check comfortably.">
  <link rel="canonical" href="http://127.0.0.1:{port}/good">
  <script type="application/ld+json">{{"@type": "Article", "headline": "Test"}}</script>
</head>
<body>
  <h1>Main Heading</h1>
  <p>{filler}</p>
  <img src="a.jpg" alt="A description">
  <a href="/internal">Internal link</a>
  <a href="https://external.example.com">External link</a>
</body>
</html>
"""

BAD_HTML = """
<html>
<head></head>
<body><p>Too short.</p></body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        port = self.server.server_address[1]
        if self.path == "/good":
            body = GOOD_HTML.format(port=port, filler="word " * 250)
        else:
            body = BAD_HTML
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):
        pass


def _start_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_good_page_scores_highly():
    server = _start_server()
    port = server.server_address[1]
    try:
        result = crawl_page(f"http://127.0.0.1:{port}/good")
        assert result.status_code == 200
        assert result.title is not None
        assert result.h1_count == 1
        assert result.has_structured_data is True
        assert result.images_missing_alt == 0
        score = score_page(result)
        assert score >= 80
    finally:
        server.shutdown()


def test_bad_page_flags_issues_and_scores_low():
    server = _start_server()
    port = server.server_address[1]
    try:
        result = crawl_page(f"http://127.0.0.1:{port}/bad")
        codes = {issue["code"] for issue in result.issues}
        assert "missing_title" in codes
        assert "missing_h1" in codes
        assert "thin_content" in codes
        score = score_page(result)
        assert score < 60
    finally:
        server.shutdown()


def test_unreachable_url_does_not_raise():
    result = crawl_page("http://127.0.0.1:1/nope")
    assert result.error is not None
    assert score_page(result) == 0
