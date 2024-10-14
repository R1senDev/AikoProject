from http.server import BaseHTTPRequestHandler, HTTPServer
from threading   import Thread
from json        import loads, dump
from time        import sleep
from os.path     import exists
from .AikoState   import aiko_state

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        '''
        This handler is bullshit, I know.
        That's no need to say this information to me.
        '''

        path = f'AikoFrontend{self.path}'
        print(path)
        if not exists(path):
            _path = path + '.html'
            if exists(_path):
                with open(_path, 'rb') as file:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                with open('AikoFrontend/errors/404.html', 'rb') as file:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(file.read())
        else:
            with open(path, 'rb') as file:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(file.read())

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        print(content_length)
        data = loads(self.rfile.read(content_length))

        print(data)
        if data['action'] == 'config':
            data['payload']['age'] = int(data['payload']['age'])
            if data['payload']['age'] < 16:
                del data['payload']['age'] # shhh..
            with open('data/userinfo.json', 'w') as file:
                dump(data['payload'], file, indent = 4)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            return
        elif data['action'] == 'activate':
            aiko_state.agreement_mutex.release()
        elif data['action'] == 'prompt':
            aiko_state.is_thinking = True
            aiko_state.chat_queue.append(data['payload'])
            print('Backend is sleeping')
            while aiko_state.is_thinking:
                sleep(0.1)
            print('Backend is awake')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(aiko_state.last_response, encoding = 'utf-8'))

server = HTTPServer(('0.0.0.0', 5050), RequestHandler)

def run(headless: bool = False) -> None:
    global thr
    thr = Thread(
        target = server.serve_forever,
        args   = (),
        daemon = True,
        name   = 'AikoGUIBackend'
    )
    thr.start()
    print(f'Started GUI on port {server.server_port}{" (headless!)" if headless else ""}')

if __name__ == '__main__':
    run(headless = True)
    while True:
        sleep(10)