#!/usr/bin/python
# -*- coding: utf-8 -*-
from bottle import request, Bottle
from wsgi import WebSocketHandler
from sl import *
from time import sleep

app = Bottle()


@app.route('/')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        return 'Hello World!'
    while True:
        message = wsock.receive()
        print message
        wsock.send('Your message was: %r' % message)
        sleep(3)
        wsock.send('Your message was: %r' % message)


        # break

def make_server(application):
    server = ThreadingWSGIServer(('', 9001), WebSocketHandler)
    server.set_app(application)
    return server


httpd = make_server(app)
print 'WSGIServer: Serving HTTP on port 9001 ...\n'
try:
    httpd.serve_forever()
except:
    print '    WSGIServer: Server Stopped'
