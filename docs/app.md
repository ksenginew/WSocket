## App

Event based app for websocket communication. This is app that uses [Framework](framework.md). If not events handled by developer. this app works like demo(echo) app.
This is a [WSGI](http://www.wsgi.org/) web app. So you can use any [WSGI](http://www.wsgi.org/) Server to host this app
> you should use HTTP version `1.1` Server with your [WSGI](http://www.wsgi.org/) framework for some clients like Firefox browser

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
> for more info on `client` see - https://github.com/Ksengine/WSocket/tree/master/docs/websocket.md


## `class  WSocketApp(app=None, protocol=None)`
`app` should be a valid [WSGI](http://www.wsgi.org/) web application.
`protocol` is websocket sub protocol to accept (ex: [WAMP](https://wamp-proto.org/))

### Class variables

`GUID` - unique ID to generate websocket accept key

`SUPPORTED_VERSIONS` - 13, 8 or 7

`websocket_class` - `"wsgi.websocket"` in WSGI Environ

### Events

`onconnect` - fires when client sent a message
`onmessage` - fires when client sent a message
`onmessage` - fires when client sent a message

you can attach event handler method to event using
- `+=` operator 
```python
app = WSocketApp()
app.onmessage += on_message
app.onmessage += on_message2
# both `on_message` and `on_message2` can handle event
run(app)
```

- `+` operator
```python
app = WSocketApp()
app.onmessage + on_message
app.onmessage + on_message2
# both `on_message` and `on_message2` can handle event
run(app)
``` 

- `=` operator
```python
app = WSocketApp()
app.onmessage = on_message
# only `on_message` can handle event
app.onmessage = on_message2
# now, only `on_message2` can handle event
run(app)
``` 
> You can't add new handlers to Event after `=` operator used. It replaces Event. But you can replace it again using another handler.
