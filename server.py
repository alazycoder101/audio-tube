import http.server
import socketserver
import os
import threading

HOST = '0.0.0.0'
PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'views/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

Handler = CustomHTTPRequestHandler
class HTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, Handler):
        self.allow_reuse_address = True
        socketserver.TCPServer.__init__(self, server_address, Handler, False)

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    server.server_bind()
    server.server_activate()
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print("serving at port", PORT)