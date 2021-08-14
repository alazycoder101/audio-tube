import http.server
import socketserver
import os
import threading
import sys

HOST = '0.0.0.0'
PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def render(self, file):
        try:
            enc = sys.getfilesystemencoding()
            file_to_open = "File not found: " + self.path[1:]
            self.send_response(404)
            enc = sys.getfilesystemencoding()
            file_to_open = open(file).read()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=%s" % enc)
        except:
            file_to_open = "File not found: " + self.path[1:]
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_GET(self):
        if self.path == '/':
            self.path = '/views/index.html'
        self.render(self.path[1:])

    def do_POST(self):
        if self.path == '/upload':
            r, info = self.deal_upload()
        if not r:
            self.render('error')

    def deal_upload(self):
        content_type = self.headers['content-type']

        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")
                
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpected Ends of data.")

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