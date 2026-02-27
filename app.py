import html
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from bls_client import fetch_bls_data

DEFAULT_KEY = os.environ.get("BLS_REGISTRATION_KEY", "f13fb030464043779475304f2e82c979")


def render_page(form, series_data=None, error=None):
    def esc(value):
        return html.escape(str(value or ""))

    sections = [
        """<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <title>BLS Data Puller</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; max-width: 900px; }
    form { display: grid; gap: 0.75rem; margin-bottom: 1.5rem; }
    label { display: grid; gap: 0.25rem; }
    input { padding: 0.4rem; font-size: 1rem; }
    button { width: fit-content; padding: 0.5rem 1rem; }
    .error { color: #b30000; margin-bottom: 1rem; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }
    th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }
    th { background-color: #f5f5f5; }
    code { background: #f1f1f1; padding: 0.1rem 0.3rem; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>BLS Data Puller</h1>
  <p>Enter one or more BLS series IDs (comma-separated), a year range, and a registration key.</p>
  <form method='post'>
    <label>Series IDs <input name='series_ids' value='"""
    ]
    sections.append(esc(form.get("series_ids")))
    sections.append("""' required /></label>
    <label>Start Year <input name='start_year' type='number' value='""")
    sections.append(esc(form.get("start_year")))
    sections.append("""' required /></label>
    <label>End Year <input name='end_year' type='number' value='""")
    sections.append(esc(form.get("end_year")))
    sections.append("""' required /></label>
    <label>Registration Key <input name='registration_key' value='""")
    sections.append(esc(form.get("registration_key")))
    sections.append("""' required /></label>
    <button type='submit'>Fetch Data</button>
  </form>
""")

    if error:
        sections.append(f"<p class='error'><strong>Error:</strong> {esc(error)}</p>")

    if series_data:
        for series in series_data:
            sections.append(f"<h2>Series: <code>{esc(series.get('seriesID'))}</code></h2>")
            sections.append(
                "<table><thead><tr><th>Year</th><th>Period</th><th>Value</th></tr></thead><tbody>"
            )
            for row in series.get("data", []):
                sections.append(
                    "<tr>"
                    f"<td>{esc(row.get('year'))}</td>"
                    f"<td>{esc(row.get('periodName'))}</td>"
                    f"<td>{esc(row.get('value'))}</td>"
                    "</tr>"
                )
            sections.append("</tbody></table>")

    sections.append("</body></html>")
    return "".join(sections)


class Handler(BaseHTTPRequestHandler):
    def _send_html(self, html_body):
        body = html_body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        form = {
            "series_ids": "CUUR0000SA0",
            "start_year": "2023",
            "end_year": "2024",
            "registration_key": DEFAULT_KEY,
        }
        self._send_html(render_page(form=form))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_data = self.rfile.read(content_length).decode("utf-8")
        parsed = parse_qs(raw_data)

        form = {
            "series_ids": parsed.get("series_ids", [""])[0].strip(),
            "start_year": parsed.get("start_year", [""])[0].strip(),
            "end_year": parsed.get("end_year", [""])[0].strip(),
            "registration_key": parsed.get("registration_key", [""])[0].strip(),
        }

        series_data = None
        error = None

        try:
            series_ids = [s.strip() for s in form["series_ids"].split(",") if s.strip()]
            if not series_ids:
                raise ValueError("Provide at least one BLS series ID.")

            series_data = fetch_bls_data(
                series_ids=series_ids,
                start_year=int(form["start_year"]),
                end_year=int(form["end_year"]),
                registration_key=form["registration_key"],
            )
        except Exception as exc:
            error = str(exc)

        self._send_html(render_page(form=form, series_data=series_data, error=error))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 5000), Handler)
    print("Serving on http://0.0.0.0:5000")
    server.serve_forever()
