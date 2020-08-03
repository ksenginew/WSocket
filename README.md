# WSocket
**HTTP and Websocket both supported wsgi server**

**Note:**
I am a student.I have no enough knowladge. So can anyone [help me](https://github.com/Ksengine/WSocket/issues/2) to develop this?

[![Downloads](https://pepy.tech/badge/wsocket)](https://pepy.tech/project/wsocket)

Server(WSGI) creates and listens at the HTTP
socket, dispatching the requests to a handler. 
this is only use standard python libraries. 
also: 
this is a plugin to ServerLight Framework.

**for a better experiense install [servelight](https://www.github.com/Ksengine/ServeLight)**

###Code to create and run the server looks like this:\
using bottle(install bottle before try)
ref: [bottlepy](https://bottlepy.org/docs/0.12/async.html?highlight=websocket#finally-websockets)
```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
from bottle import request, Bottle
from wsocket import WebSocketHandler, WebSocketError
from wsgiref.simple_server import make_server
from time import sleep

app = Bottle()

@app.route('/')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        return 'Hello World!'

    while True:
        try:
            message = wsock.receive()
            print(message)
            wsock.send('Your message was: %r' % message)
            sleep(3)
            wsock.send('Your message was: %r' % message)
        except WebSocketError:
            break        


httpd = make_server('localhost',9001,app,handler_class=WebSocketHandler)
print('WSGIServer: Serving HTTP on port 9001 ...\n')
try:
    httpd.serve_forever()
except:
    print('WSGIServer: Server Stopped')

```
run this code
download [client.html](https://github.com/Ksengine/WSocket/blob/master/client.html) file
open it with browser
see how it works!
then navigate to http://localhost:9001
You can see
    Hello World!
### Features
 - the power of websocket
 - fast ( It's very fast )
 - simple
 - lightweight (simple and lightweight )
 -  [WSGI](http://www.wsgi.org/) ( supports web server gateway interface )
 - with web frameworks (any  [WSGI](http://www.wsgi.org/)  framework supported)
 
> Flask, Django, Pyramid, Bottle supported

[**View Documentaion***](https://servelight2020.gitbook.io/docs/)
[report bugs](https://github.com/Ksengine/WSocket/issues/new/choose)
### License
Code and documentation are available according to the MIT License (see  [LICENSE](https://github.com/Ksengine/WSocket/blob/master/LICENSE)).
