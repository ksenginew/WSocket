
# Websocket
### Class variables
- `origin` - HTTP `Origin` header

- `protocol` - supported websocket sub protocol

- `version` - websocket version(1, 8 or 7)

- `path` - required path by client(eg:-if websocket url which client opened is `ws://localhost/hello/world?user=Ksengine&pass=1234`, path is `/hello/world`)

- `logger` = default logger([Python Docs](https://docs.python.org/3/library/logging.html))

- `do_compress` - is compressed messages required by client

### Class methods
