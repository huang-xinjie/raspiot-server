import json
import uuid
import socket
import http.server
import socketserver
import urllib.parse
import urllib.request


class WebCamera(object):

    class HttpHandler(http.server.BaseHTTPRequestHandler):
        port = 8085
        web_cam = None

        def do_GET(self):
            if self.path == '/details':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                details = self.web_cam.get_details()
                self.wfile.write(json.dumps(details).encode())
            else:
                self.send_error(404, 'Resource not found')

        def do_PUT(self):
            if self.path not in ['/detail']:
                self.send_error(404, 'Resource not found')
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            req_body = json.loads(body)
            print(f'set detail request: {req_body}')

            self.web_cam.set_value(req_body.get('value'))
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            details = self.web_cam.get_details()
            self.wfile.write(json.dumps(details).encode())

    def __init__(self):
        self.mac_addr = self.get_mac()
        self.ip_addr = self.get_ip()
        self.value = False
        self.HttpHandler.web_cam = self

    @staticmethod
    def get_mac():
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    @staticmethod
    def get_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            return ip
        finally:
            s.close()

    def set_value(self, value):
        self.value = value

    def get_details(self):
        details = [{"type": "text",
                    "name": "ip addr",
                    "value": f"{self.ip_addr}"},
                   {"type": "switch",
                    "name": "switch",
                    "value": self.value},
                   {"type": "button",
                    "name": "button",
                    "value": "press"}]
        return details

    def access_raspiot(self):
        payload = {'mac_addr': self.mac_addr,
                   'ipv4_addr': self.ip_addr,
                   'port': self.HttpHandler.port}
        data = urllib.parse.urlencode(payload).encode('utf-8')
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        req = urllib.request.Request('http://127.0.0.1/device/access', data=data, headers=headers)
        res = urllib.request.urlopen(req)

        access_response = res.read()
        print(f'access_response: {json.loads(access_response)}')

    def run(self):
        self.access_raspiot()
        with socketserver.TCPServer(('', WebCamera.HttpHandler.port), WebCamera.HttpHandler) as httpd:
            print(f'listening at {WebCamera.get_ip()}:{WebCamera.HttpHandler.port}')
            httpd.serve_forever()


if __name__ == '__main__':
    web_cam = WebCamera()
    web_cam.run()
