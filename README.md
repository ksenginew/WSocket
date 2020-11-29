# <img src="https://github.com/Ksengine/WSocket/raw/master/assests/icon.png" width="30" height="30"> WSocket
**Simple WSGI HTTP + Websocket Server, Framework, Middleware And App.**

[![Downloads](https://pepy.tech/badge/wsocket)](https://pepy.tech/project/wsocket)

**Note:**
I am a 16 years old student.I have no enough knowledge. So can anyone [help me](https://github.com/Ksengine/WSocket/issues/2) to develop this library?

## Install
You can
- Installing from PyPI
- Download and Include

### Installing from PyPI
Install latest version or upgrade an already installed WSocket to the latest from PyPI.
```bash
pip install --upgrade wsocket
```
### Download and Include
- Visit [wsocket.py](https://raw.githubusercontent.com/Ksengine/WSocket/master/wsocket.py/).
- Save file (`ctrl+s` in browser).
- Include in your package derectory.
```
    my-app/
    ├─ hello_world.py
    ├─ wsocket.py
```
## Getting Started
- Include following source on your test file(eg:-`hello_world.py`).
```python
from wsocket import WSocketApp, WebSocketError, logger, run
from time import sleep

logger.setLevel(10)  # for debugging

def on_close(self, message, client):
    print(repr(client) + " : " + message)

def on_connect(client):
    print(repr(client) + " connected")

def on_message(message, client):
    print(repr(clent) + " : " + repr(message))
    try:
        client.send("you said: " + message)
        sleep(2)
        client.send("you said: " + message)

    except WebSocketError:
        pass

app = WSocketApp()
app.onconnect += on_connect
app.onmessage += on_message
app.onclose += on_close

run(app)
```
- Visit [client.html](https://github.com/Ksengine/WSocket/raw/master/client.html).
- Save file (`ctrl+s` in browser).
- Open it in browser(websocket supported).
- Experience the two way websocket communication. :smile::smile::smile:

## Introduction
### Server
Server([WSGI](http://www.wsgi.org/)) creates and listens at the HTTPsocket, dispatching the requests to a handler. WSGIRef server but uses threads to handle requests by using the ThreadingMixIn. This is useful to handle web browsers pre-opening sockets, on which Server would wait indefinitely.
**can used with any WSGI compatible web framework**

### Middleware
convert any WSGI compatible web framework to Websocket+HTTP framework
using middleware.
**works with many WSGI compatible servers**
**can used with any WSGI compatible web framework**
> Flask, Django, Pyramid, Bottle, ... supported

### Handler
`wsgiref.simple_server.WSGIRequestHandler`  like class named `FixedHandler`  that always wrap WSGI app using Middleware.
changes from `WSGIRequestHandler` :
- Prevents reverse DNS lookups
- errorless logger
- use `ServerHandler`  to make it WSGI

> You can convert wsgiref to a websocket+HTTP server using this handler

#### ServerHandler
`wsgiref.simple_server.ServerHandler`(inherited from `wsgiref.handlers.ServerHandler` like handler named `FixedServerHandler` .
changes from `ServerHandler` :
- set HTTP version to `1.1` because versions below `1.1` are not supported some clients like Firefox.
- removed hop-by-hop headers checker because it raise errors on `Upgrade`  and `Connection` headers
- check that all headers are strings

### Framework
basic WSGI web application framework that uses Middleware.
- simple routes handler
- auto description to status code
- headers checker
- send data as soon as possible
- send strings, bytes, lists(even bytes and strings mixed) or files directly 
- error catcher and error logger

**works with many WSGI compatible servers**

### App
Event based app for websocket communication. this is app that uses Framework
if not events handled by developer. this app works like demo(echo) app.

## Features
all Middleware, Handler, Framework and App has following features.
- websocket sub protocol supported
- websocket message compression supported (works if client asks)
- receive and send pong and ping messages(with automatic pong sender)
- receive and send binary or text messages
- works for messages with or without mask
- closing messages supported
- auto and manual close

**View Documentaion** - https://wsocket.gitbook.io/

**Report Bugs** - https://github.com/Ksengine/WSocket/issues/new/

## License
Code and documentation are available according to the MIT License (see  [LICENSE](https://github.com/Ksengine/WSocket/blob/master/LICENSE)).
