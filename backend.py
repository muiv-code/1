from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        # Без этого хедера не работает с фронтом.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # TODO: replace with data from db.
        options = {
            "motherboard": ["1", "2", "3"],
            "cpu": ["4", "5", "6"],
            "mem": ["7", "8", "9"],
            "hd": ["10", "11", "12"],
            "gpu": ["13", "14", "15"],
            "power": ["16", "17", "18"],
            "case": ["19", "20", "21"]
        }

        optionsJson = json.dumps(options)
        self.wfile.write(str.encode(optionsJson))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        # Без этого хедера не работает с фронтом.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # TODO: send to db.
        print(body)

httpd = HTTPServer(('localhost', 9099), SimpleHTTPRequestHandler)
httpd.serve_forever()