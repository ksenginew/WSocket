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


## About The Project

This is a simple library to add websocket support to WSGI.

- Server - Patched wsgiref server
- Middleware - Add websocket support to Flask, Django, Pyramid, Bottle, ...
- Handler - Websocket handler to wsgiref
- Framework - Basic websocket + WSGI web application framework
- App - Plug and play demo app.

## Getting Started

This is an example of how you may give instructions on setting up your websocket connunication locally. 

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
**Report Bugs** - https://github.com/Ksengine/WSocket/issues/new/
