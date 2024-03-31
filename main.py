import json
import socket
import pathlib
import mimetypes
import urllib.parse
from threading import Thread
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler


SOKET_IP = "localhost"
SOKET_PORT = 5000

HTTP_IP = "localhost"
HTTP_PORT = 3000

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        run_socket_client(SOKET_IP, SOKET_PORT, data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('front-init/index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('front-init/message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('front-init/error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run_HTTP(ip, port):
    server_address = (ip, port)
    with (HTTPServer(server_address, HttpHandler)) as http:
        http.serve_forever()

def run_socket_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server = ip, port
        sock.bind(server)
        while True:
            data, address = sock.recvfrom(1024)
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            time = datetime.now()
            json_dict = {str(time):data_dict}
            with open("front-init/storage/data.json", "a") as json_file:
                json.dump(json_dict, json_file, indent=4)

def run_socket_client(ip, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server = ip, port
        sock.sendto(data, server)

if __name__ == '__main__':
    http = Thread(target=run_HTTP, args=(HTTP_IP, HTTP_PORT))
    soket = Thread(target=run_socket_server, args=(SOKET_IP, SOKET_PORT))
    soket.start()
    http.start()

