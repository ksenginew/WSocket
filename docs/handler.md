
# Server
Server([WSGI](http://www.wsgi.org/)) creates and listens at the HTTP socket, dispatching the requests to a handler. WSGIRef server but uses threads to handle requests by using the ThreadingMixIn. This is useful to handle web browsers pre-opening sockets, on which Server would wait indefinitely.  **can used with any WSGI compatible web framework**
> this is a wsgiref based server

[`wsgiref`](https://docs.python.org/3/library/wsgiref.html "(in Python v3.x)")  is a built-in WSGI package that provides various classes and helpers to develop against WSGI. Mostly it provides a basic WSGI server that can be used for testing or simple demos. WSocket provides support for websocket on wsgiref for testing purpose. It can only initiate connections one at a time, as a result of being single threaded. 
**but WSocket WSGI server is multi threaded HTTP server. So it can handle many  connections at a time.**

## `wsocket.run(app=WSocketApp(), host="127.0.0.1", port=8080, handler_cls=FixedHandler, server_cls=ThreadingWSGIServer)`
if app not given it runs demo app
you can use following values as `host` to run local server(named localhost)
- `"localhost"`
- `"127.0.0.1"`
- `""`

default `host` is "127.0.0.1".
default `port` is 8080. If host is 0, It will choose random port
default `handler_cls` is [`FixedHandler`](handler.md)
default `server_cls` is [`ThreadingWSGIServer`](#`wsocket.ThreadingWSGIServer`)
`app` should be a valid [WSGI](http://www.wsgi.org/) application.
**example :**
```python
from wsocket import run, WSocketApp
app = WSocketApp()
run('', 8080, app)
```

## `wsocket.make_server(host,  port,  app, server_class,  handler_class)`
Create a new WSGIServer server listening on  _host_  and  _port_, accepting connections for  _app_. The return value is an instance of the supplied  _server_class_, and will process requests using the specified  _handler_class_.  _app_  must be a WSGI application object, as defined by  [**PEP 3333**](https://www.python.org/dev/peps/pep-3333).

**example :**
```python
from wsocket import WebSocketHandler, WSocketApp, make_server, ThreadingWSGIServer

server = make_server('', 8080, server_class=ThreadingWSGIServer,
                     handler_class=WebSocketHandler,
                     app=WSocketApp())
server.serve_forever()
```

## `wsocket.ThreadingWSGIServer(server_address, RequestHandlerClass)`
Create a  `ThreadingWSGIServer` instance.  _server_address_  should be a  `(host,port)`  tuple, and  _RequestHandlerClass_  should be the subclass of  [`http.server.BaseHTTPRequestHandler`](https://docs.python.org/3/library/http.server.html#http.server.BaseHTTPRequestHandler "http.server.BaseHTTPRequestHandler")  that will be used to process requests.

You do not normally need to call this constructor, as the  [`make_server()`](#make_server)  function can handle all the details for you.

 `ThreadingWSGIServer` is a subclass of  [`WSGIServer`](https://docs.python.org/3/library/wsgiref.html#wsgiref.simple_server.WSGIServer "wsgiref.simple_server.WSGIServer").  [`ThreadingWSGIServer`] also provides these WSGI-specific methods:

`set_app(application)` - Sets the callable  _application_  as the WSGI application that will receive requests.

`get_app()` - Returns the currently-set application callable.

Normally, however, you do not need to use these additional methods, as  [`set_app()`]  is normally called by  [`make_server()`](#make_server), and the  [`get_app()`]  exists mainly for the benefit of request handler instances.
