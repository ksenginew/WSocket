from bottle import request, Bottle
from wsocket import WebSocketHandler,logger
from sl.server import ThreadingWSGIServer
from time import sleep
logger.setLevel(10)
app = Bottle()

@app.route('/')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        return 'Hello World!'
    while True:
        message = wsock.receive()
        if not message:
            break
        print(message)
        wsock.send('Your message was: %r' % message)
        sleep(3)
        wsock.send('Your message was: %r' % message)

httpd = ThreadingWSGIServer(('localhost',9001),WebSocketHandler)
httpd.set_app(app)
print('WSGIServer: Serving HTTP on port 9001 ...\n')
try:
    httpd.serve_forever()
except:
    print('WSGIServer: Server Stopped')
