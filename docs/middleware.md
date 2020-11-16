## Middleware

convert any WSGI compatible web framework to Websocket+HTTP framework using middleware.  **works with many WSGI compatible servers** 

**can used with any [WSGI](http://www.wsgi.org/) compatible web framework**
> Flask, Django, Pyramid, Bottle, ... supported

This middleware adds [`wsgi.websocket`](https://github.com/Ksengine/WSocket/tree/master/docs/websocket.md) variable to [WSGI](http://www.wsgi.org/) environment dictionary.

example with [bottle](https://github.com/bottlepy/bottle):
```python
from bottle import request, Bottle
from wsocket import WSocketApp, WebSocketError, logger, run
from time import sleep

logger.setLevel(10)  # for debugging

bottle = Bottle()
app = WSocketApp(bottle)
# app = WSocketApp(bottle, "WAMP")

@bottle.route("/")
def handle_websocket():
    wsock = request.environ.get("wsgi.websocket")
    if not wsock:
        return "Hello World!"

    while True:
        try:
            message = wsock.receive()
            if message != None:
                print("participator : " + message)
            wsock.send("you : "+message)
            sleep(2)
            wsock.send("you : "+message)
        except WebSocketError:
            break
run(app)
```
> you should use HTTP version `1.1` Server with your [WSGI](http://www.wsgi.org/) framework for some clients like Firefox browser

**for examples on other web frameworks visit [`examples/frameworks`](https://github.com/Ksengine/WSocket/tree/master/examples/frameworks) folder
## `class  WSocketApp(app=None, protocol=None)`
`app` should be a valid [WSGI](http://www.wsgi.org/) web application.
`protocol` is websocket sub protocol to accept (ex: [WAMP](https://wamp-proto.org/))

### Class variables

`GUID` - unique ID to generate websocket accept key

`SUPPORTED_VERSIONS` - 13, 8 or 7

`websocket_class` - `"wsgi.websocket"` in WSGI Environ
