from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

MAX_SIZE = 20 * 1024 * 1024
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/convert':
            return self.send_error(404)
        try:
            size = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.send_error(400, 'Invalid content length')
        if size < 8 or size > MAX_SIZE:
            return self.send_error(413, 'File must be at most 20 MB')
        self.connection.settimeout(30)
        data = self.rfile.read(size)
        if len(data) != size or not data.startswith(bytes.fromhex('d0cf11e0a1b11ae1')):
            return self.send_error(400, 'Not a valid legacy Word document')
        try:
            with TemporaryDirectory(prefix='wordreader-') as tmp:
                root = Path(tmp)
                source = root / 'input.doc'
                source.write_bytes(data)
                result = subprocess.run(['/usr/bin/libreoffice', '-env:UserInstallation=' + (root / 'profile').as_uri(), '--headless', '--convert-to', 'docx:Office Open XML Text', '--outdir', tmp, str(source)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                output = root / 'input.docx'
                if result.returncode != 0 or not output.is_file() or output.stat().st_size > MAX_SIZE * 2:
                    return self.send_error(422, 'Could not convert document; it may be damaged or password protected')
                converted = output.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Length', str(len(converted)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(converted)
        except (OSError, subprocess.TimeoutExpired):
            self.send_error(500, 'Document conversion failed')
    def log_message(self, format, *args):
        pass
HTTPServer(('127.0.0.1', 8793), Handler).serve_forever()
