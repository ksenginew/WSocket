[![Downloads](https://static.pepy.tech/personalized-badge/wsocket?period=total&units=none&left_color=black&right_color=blue&left_text=downloads)](https://pepy.tech/project/wsocket) 
 [![GitHub issues](https://img.shields.io/github/issues/Ksengine/WSocket?style=flat-square)](https://github.com/Ksengine/WSocket/issues) 
 [![GitHub forks](https://img.shields.io/github/forks/Ksengine/WSocket?style=flat-square)](https://github.com/Ksengine/WSocket/network) 
 [![GitHub stars](https://img.shields.io/github/stars/Ksengine/WSocket?style=flat-square)](https://github.com/Ksengine/WSocket/stargazers) 
 [![GitHub license](https://img.shields.io/github/license/Ksengine/WSocket?style=flat-square)](https://github.com/Ksengine/WSocket/blob/master/LICENSE) 
 [![Twitter](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2FKsengine%2FWSocket)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FKsengine%2FWSocket) 

<br />
<p align="center">
  <a href="https://github.com/Ksengine/WSocket">
    <img src="https://github.com/Ksengine/WSocket/raw/master/assests/icon.png" alt="Logo" width="100" height="80">
  </a>

  <h1 align="center">WSocket</h1>

  <p align="center">
    <b>Simple WSGI HTTP + Websocket Server, Framework, Middleware And App.</b>
    <br />
    <br />
    <a href="https://github.com/Ksengine/WSocket"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://pypi.org/project/WSocket">PyPI</a>
    ·
    <a href="https://github.com/Ksengine/WSocket/issues">Report Bug</a>
    ·
    <a href="https://github.com/Ksengine/WSocket/issues">Request Feature</a>
  </p>
</p>


<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#server">Server</a></li>
        <li><a href="#middleware">Middleware</a></li>
        <li><a href="#handler">Handler</a></li>
        <li><a href="#framework">Framework</a></li>
        <li><a href="#app">App</a></li>
      </ul>
    </li>
        <li><a href="#features">Features</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


## About The Project

There are many great WebSocket libraries available on GitHub:octocat:, 
however, I didn't find one that really suit my needs so I created this enhanced one. 

Here's why:
- **Use with any server** - WSocket supports any WSGI server(with patches). and patched `wsgiref` server already included. 
- **Use with any web framework** - WSocket supports any WSGI framework. and basic web framework already included. 
- **Plug :electric_plug: and Play :arrow_forward:** - use WSocket app

**Note:** I am a 16 years old student.I have no enough knowledge. So can anyone [help me](https://github.com/Ksengine/WSocket/issues/2) to develop this library?

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


## Getting Started

This is an example of how you may give instructions on setting up your websocket connunication locally. 

### Prerequisites

run following command on your command prompt/ console.
```bash
python -c "import wsgiref"
```

If no result printed, jump to [Installation section](#Installation)

if you can see following error
```python
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'wsgiref'
```

run following command on your command prompt/ console.
```bash
pip install wsgiref
```

### Installation
You can
- Installing from PyPI
- Download:down_arrow: and Include

#### Installing from PyPI

Install latest version or upgrade an already installed WSocket to the latest from PyPI.
```bash
pip install --upgrade wsocket
```

#### Download and Include

- Visit [wsocket.py](https://raw.githubusercontent.com/Ksengine/WSocket/master/wsocket.py/).
- Save file (`ctrl+s` in browser).
- Include in your package derectory.
```
    my-app/
    ├─ hello_world.py
    ├─ wsocket.py
```
**Report Bugs** - https://github.com/Ksengine/WSocket/issues/new/


## Usage

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

**View Documentaion** - https://wsocket.gitbook.io/

**Report Bugs** - https://github.com/Ksengine/WSocket/issues/new/


## Roadmap

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a list of proposed features (and known issues).


## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## License
Code and documentation are available according to the MIT License (see  [LICENSE](https://github.com/Ksengine/WSocket/blob/master/LICENSE)).


## Contact
**View Documentaion** - https://wsocket.gitbook.io/

**Report Bugs** - https://github.com/Ksengine/WSocket/issues/new/
