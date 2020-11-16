# Framework

basic WSGI web application framework that uses Middleware.

-   simple routes handler
-   auto description to status code
-   headers checker
-   send data as soon as possible
-   send strings, bytes, lists(even bytes and strings mixed) or files directly
-   error catcher and error logger

**works with many WSGI compatible servers**
> you should use HTTP version **`1.1`** Server with your [WSGI](http://www.wsgi.org/) framework for some clients like Firefox browser

```python
from wsocket import WSocketApp, WebSocketError, logger, run
from time import sleep

logger.setLevel(10)  # for debugging

app = WSocketApp()
# app = WSocketApp(protocol="WAMP")

@app.route("/")
def handle_websocket(environ, start_response):
    
    wsock = environ.get("wsgi.websocket")

    if not wsock:
        start_response()
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
> more info on `wsgi.websocket` variable in [WSGI](http://www.wsgi.org/) environment dictionary - https://github.com/Ksengine/WSocket/tree/master/docs/websocket.md

## `class  WSocketApp(app=None, protocol=None)`


### Class variables

`GUID` - unique ID to generate websocket accept key

`SUPPORTED_VERSIONS` - 13, 8 or 7

`routes` - dictionary for route handlers

`websocket_class` - `"wsgi.websocket"` in WSGI Environ


### Methods

`not_found(self, environ, start_response)` - handle `404 NOT FOUND` error

`route(self, r)` - register routes

## Routes
WSocket uses simple routes engine.
How it works?
- URL -  `http://localhost:8080/hello/world?user=Ksengine&pass=1234`
- divided into parts(by Server)
    | origin | host      | port | path         | query                   |
    |--      |--         |--    |--            |--                       |
    | `http`   | `localhost` | `8080` | `/hello/world` | `user=Ksengine&pass=1234` |
    **only path is used to find routes**
- walk through routes dictionary
  - if `"/hello/world"` path found, trigger route handler
    ```python
    @app.route("/hello/world")
      ```
   - else, if some route string ends with "*" and path starts with that string trigger route handler 
       ```python
      @app.route("/hello/world")
      ```
  
## Status and Headers
call `start_response` to send status code and headers.
if you returns without calling it. It will send `200 OK` status and some basic headers to client.
if `start_response` is called without argsuments, it will send `200 OK` status and some basic headers to client.
```python
start_response()
```
`start_response` has two arguments
- status - status code as int(eg:-200) or str(eg:- "200 OK" or "200"). If status description(eg:-"OK") not supplied, it will find it.
- headers - HTTP headers. can passed as,
  - list of tuples 
     ```python
    [("header1 name", "header1 value"),
    ("header2 name", "header2 value")  ]
     ```
  - dictionary
     ```python
    {"header1 name": "header1 value",
    "header2 name": "header2 value"}
    ```

status code examples:-
```python
start_response() # start_response("200 OK",[])
```
```python
start_response(200) # start_response("200 OK",[])
```
```python
start_response("200") # start_response("200 OK",[])
```
```python
start_response("200 OK") # start_response("200 OK",[])
```
send headers examples:-
- list of tuples 
     ```python
    start_response("200 OK",[
        ("header1 name", "header1 value"),
        ("header2 name", "header2 value")
  ])
    ```
    
- dictionary
    ```python
   start_response("200 OK",{
    "header1 name": "header1 value",
    "header2 name": "header2 value"
  })
  ```

## Send data
You can send following data types
- `str` - string, text
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return "Hello World!"
  ```
- `bytes` - binary
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return b"Hello World!" # b"" is binary string
  ```
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return "Hello World!".encode() # str.encode converts str to bytes
  ```
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return b"Hello World!" # open file as text file
  ```
- `files` - opened files
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return open("hello.txt")
  ```
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return open("hello.txt", "b") # "b" - open as binary file
  ```
- `file-like object` - streams(text, binary) like `StringIO`or `BytesIO`
   ```python
   try:
       from io import StringIO
   except ImportError:
       from StringIO import StringIO
   
  def sender(environ, start_response)
      start_response()
      # ...some code here
      file_like = StringIO()
      return file_like
  ```
     ```python
   try:
       from io import BytesIO
   except ImportError:
       from StringIO import BytesIO
   
  def sender(environ, start_response)
      start_response()
      # ...some code here
      file_like = BytesIO()
      return file_like
  ```
- `iterables`  - `list`,  `tuple`, `set` `dict` `generators` etc.
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return ["Hello ", b"World", "!".encode(), 2020] # list
  ```
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return ("Hello ", b"World", "!".encode(), 2020) # tuple
  ```
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return {"Hello ", b"World", "!".encode(), 2020} # set
  ```
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return {"Hello ":None, "World!":None} # dict
  ```
   ```python
   import time
  def sender(environ, start_response)
      start_response()
      # ...some code here
      yield "Hello "
      time.sleep(2)
      yield b"World"
      time.sleep(5)
      yield "!".encode()
      yield 2020 # generators
  ```
  **generators can send data one by one with time intervals. so it's like async Server**
- other - 
   ```python
  def sender(environ, start_response)
      start_response()
      # ...some code here
      return 3.3 # float
  ```
 
  ## Errors
  example :-
><body><h1>Internal Server Error(500)</h1><p><b>ZeroDivisionError :division by zero</b></p><p><samp></samp></p><pre>Traceback (most recent call last):
>  File "wsocket.py", line 881, in process_response
>    results = self.app(self.environ, self.start_response)
>  File "wsocket.py", line 1068, in wsgi
>    1/0
> ZeroDivisionError: division by zero
> </pre><p></p><button><h3>report</h3></button></body>

report button starts reporting issue
and logger will print error to python console
