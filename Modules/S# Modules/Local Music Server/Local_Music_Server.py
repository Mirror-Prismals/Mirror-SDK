import http.server
import socketserver
import os
import json

PORT = 8000

# Change directory to the folder containing your music files and HTML file
os.chdir(os.path.dirname(__file__))

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Cache-Control', 'post-check=0, pre-check=0')
        self.send_header('Pragma', 'no-cache')
        http.server.SimpleHTTPRequestHandler.end_headers(self)
    
    def do_GET(self):
        if self.path == '/tracks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            tracks = [f for f in os.listdir() if f.endswith(('.mp3', '.wav', '.ogg'))]
            self.wfile.write(bytes(json.dumps(tracks), 'utf-8'))
        else:
            super().do_GET()

Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
