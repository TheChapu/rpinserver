import RPi.GPIO as GPIO
import urllib.parse
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

GPIO.setmode(GPIO.BCM)

PINS = [25, 8, 7, 1, 6, 13, 19, 26]
for pin in PINS:
    GPIO.setup(pin, GPIO.OUT)

def p_set(index, value):
    GPIO.output(PINS[index], value)

def on(index):
    p_set(index, True)

def off(index):
    p_set(index, False)

def state(index):
    return GPIO.input(PINS[index])

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _index(self):
        path = self.path.split('/')
        try:
            index = int(path[1])
            if 0 <= index < len(PINS):
                return index
            else:
                return None
        except:
            return None

    def _on_form(self, index):
        return '<form action="/{i}" method="post"><input type="hidden" name="state" value="1"><input type="submit" value="ON"></form>'.format(i=index)

    def _off_form(self, index):
        return '<form action="/{i}" method="post"><input type="hidden" name="state" value="0"><input type="submit" value="OFF"></form>'.format(i=index)

    def _form(self, index):
        if state(index):
            return self._off_form(index)
        return self._on_form(index)

    def _color(self, index):
        if state(index):
            return "yellow"
        return "grey"

    def _redirect(self):
        self.send_response(301)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self._set_headers()
            rows = '\n'.join(['<tr><td bgcolor="{color}">{i}.{form}</td></tr>'.format(i=i, form=self._form(i), color=self._color(i)) for i in range(len(PINS))])
            message = '<html><body><table border="1">{}</table></body></html>'.format(rows)
            self.wfile.write(bytes(message, "utf8"))
        else:
            index = self._index()
            if index is None:
                self.send_error(400)
            else:
                self._set_headers()
                message = "{}".format(state(index))
                self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))
        print("received: {}".format(post_data))
        try:
            if self.path == "/":
                for i in range(len(PINS)):
                    if str(i) in post_data:
                        p_set(i, int(post_data[str(i)][0]))
                self._redirect()
            else:
                index = self._index()
                if index is None:
                    self.send_error(400)
                else:
                    new_value = int(post_data["state"][0])
                    p_set(index, new_value)
                    self._redirect()
        except:
            self.send_error(400)


def run():
    server_address = ('', 80)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    httpd.serve_forever()

# Init sequence so we know we're up
for i in range(len(PINS)):
    on(i)
    time.sleep(0.2)
    off(i)

run()

