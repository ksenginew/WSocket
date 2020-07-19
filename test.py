from bottle import request, Bottle
from wsocket import WebSocketHandler
from wsgiref.simple_server import make_server
from time import sleep

app = Bottle()

@app.route('/')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        return 'Hello World!'
    while True:
        message = wsock.receive()
        print(message)
        wsock.send('Your message was: %r' % message)
        sleep(3)
        wsock.send('Your message was: %r' % message)

httpd = make_server('localhost',9001,app,handler_class=WebSocketHandler)
print('WSGIServer: Serving HTTP on port 9001 ...\n')
try:
    httpd.serve_forever()
except:
    print('WSGIServer: Server Stopped')
