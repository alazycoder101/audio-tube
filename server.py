from http.server import SimpleHTTPRequestHandler
import socketserver
import posixpath
import urllib.request, urllib.parse, urllib.error
import os
import threading
import re
import sys
import logging

import subprocess

HOST = '0.0.0.0'
PORT = 8000

def audio_to_video(file_name, mp3_file):
    outfile_name = file_name.split('.')[0] + '.mp4'
    subprocess.call('ffmpeg -i ' + file_name
                    + ' -i ' + mp3_file + ' -strict -2 -f mp4 '
                    + outfile_name, shell=True)

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def render(self, file, hash={}):
        try:
            enc = sys.getfilesystemencoding()
            file_to_open = open(file).read()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=%s" % enc)
        except:
            file_to_open = "File not found: " + self.path[1:]
            self.send_response(404)
        self.end_headers()
        content = (file_to_open % hash)
        self.wfile.write(bytes(content, 'utf-8'))

    def do_GET(self):
        if self.path == '/':
            self.path = '/views/index.html'
        self.render(self.path[1:])

    def do_POST(self):
        if self.path == '/upload':
            r, params, info = self.deal_post_data()
            if not r:
                self.render('error')
            image = params['uploads[image]']
            audio = params['uploads[audio]']
            params['video'] = audio_to_video(image, audio)

            self.render('views/uploaded.html', params)

    def deal_post_data(self):
        uploaded_files = []
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        params = {}
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            matches = re.findall(r'Content-Disposition.*name="(.*)"; filename="(.*)"', line.decode())
            if not matches:
                matches = re.findall(r'Content-Disposition.*name="(.*)"', line.decode())
                print("not a file")
                if matches:
                    name = matches[0]
                    line = self.rfile.readline()
                    remainbytes -= len(line)
                    line = self.rfile.readline()
                    remainbytes -= len(line)
                    params[name] = line
                continue
            name, file = matches[0]
            params[name] = file
            path = self.translate_path(self.path)
            fn = os.path.join(path, file)
            line = self.rfile.readline()
            remainbytes -= len(line)
            line = self.rfile.readline()
            remainbytes -= len(line)
            try:
                out = open(fn, 'wb')
            except IOError:
                return (False, None, "Can't create file to write, do you have permission to write?")
            else:
                with out:
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
                            uploaded_files.append(fn)
                            break
                        else:
                            out.write(preline)
                            preline = line
        return (True, params, "File '%s' upload success!" % ",".join(uploaded_files))


    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

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
    logging.basicConfig(level=logging.DEBUG)
