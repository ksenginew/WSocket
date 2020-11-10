#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
WSocket is a Simple WSGI Websocket Server, Framework, Middleware And 
App. It also offers a basic WSGI framework with routes handler, a 
built-in HTTP Server and event based websocket application. all in a 
single file and with no dependencies other than the Python Standard 
Library.

Homepage and documentation: https://wsocket.gitbook.io

Copyright (c) 2020, Kavindu Santhusa.
License: MIT
"""
# Imports
from __future__ import absolute_import, division, print_function

from base64 import b64decode, b64encode
from hashlib import sha1
from sys import version_info, exc_info
from threading import Thread
from time import sleep
import traceback
import logging
import zlib
import struct
import socket
from socket import error as socket_error
from wsgiref.simple_server import make_server, ServerHandler
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer

try:  # Py3
    from socketserver import ThreadingMixIn
    from urllib.parse import urlencode

except ImportError:  # Py2
    from SocketServer import ThreadingMixIn
    from urllib import urlencode
    
__author__ = "Kavindu Santhusa"
__version__ = "2.0.0.dev1"
__license__ = "MIT"
__status__ = 4 # see setup.py

logger = logging.getLogger(__name__)
logging.basicConfig()

# python compatability
PY3 = version_info[0] >= 3
if PY3:
    import http.client as httplib

    text_type = str
    string_types = (str,)
    range_type = range

else:
    import httplib

    bytes = str
    text_type = unicode
    string_types = basestring
    range_type = xrange

# websocket OPCODES
OPCODE_CONTINUATION = 0x00
OPCODE_TEXT = 0x01
OPCODE_BINARY = 0x02
OPCODE_CLOSE = 0x08
OPCODE_PING = 0x09
OPCODE_PONG = 0x0A
FIN_MASK = 0x80
OPCODE_MASK = 0x0F
MASK_MASK = 0x80
LENGTH_MASK = 0x7F
RSV0_MASK = 0x40
RSV1_MASK = 0x20
RSV2_MASK = 0x10
HEADER_FLAG_MASK = RSV0_MASK | RSV1_MASK | RSV2_MASK

# default messages
MSG_SOCKET_DEAD = "Socket is dead"
MSG_ALREADY_CLOSED = "Connection is already closed"
MSG_CLOSED = "Connection closed"

# from bottlepy/bottle
#: A dict to map HTTP status codes (e.g. 404) to phrases (e.g. 'Not Found')
HTTP_CODES = httplib.responses.copy()
HTTP_CODES[418] = "I'm a teapot"  # RFC 2324
HTTP_CODES[428] = "Precondition Required"
HTTP_CODES[429] = "Too Many Requests"
HTTP_CODES[431] = "Request Header Fields Too Large"
HTTP_CODES[451] = "Unavailable For Legal Reasons"  # RFC 7725
HTTP_CODES[511] = "Network Authentication Required"
_HTTP_STATUS_LINES = dict((k, "%d %s" % (k, v)) for (k, v) in HTTP_CODES.items())

def log_traceback(ex):
    if PY3:
        ex_traceback = ex.__traceback__
    else:
        _, _, ex_traceback = exc_info()
    tb_lines = ''
    for line in traceback.format_exception(ex.__class__, ex, ex_traceback):
        tb_lines+=str(line)
    return tb_lines


class WebSocketError(socket_error):
    """
    Base class for all websocket errors.
    """

    pass


class ProtocolError(WebSocketError):
    """
    Raised if an error occurs when de/encoding the websocket protocol.
    """

    pass


class FrameTooLargeException(ProtocolError):
    """
    Raised if a frame is received that is too large.
    """

    pass


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):

    """This class is identical to WSGIServer but uses threads to handle
    requests by using the ThreadingMixIn. This is useful to handle web
    browsers pre-opening sockets, on which Server would wait indefinitely.
    """

    multithread = True
    daemon_threads = True


class FixedServerHandler(ServerHandler):  # fixed serverhandler
    http_version = "1.1"  # http versions below 1.1 is not supported by some clients such as Firefox

    def _convert_string_type(self, value, title):  # not in old versions of wsgiref
        """Convert/check value type."""
        if isinstance(value, string_types):
            return value

        raise AssertionError(
            "{0} must be of type str (got {1})".format(title, repr(value))
        )

    def start_response(self, status, headers, exc_info=None):
        """'start_response()' callable as specified by PEP 3333"""

        if exc_info:
            try:
                if self.headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0](exc_info[1]).with_traceback(exc_info[2])

            finally:
                exc_info = None  # avoid dangling circular ref

        elif self.headers is not None:
            raise AssertionError("Headers already set!")

        self.status = status
        self.headers = self.headers_class(headers)
        status = self._convert_string_type(status, "Status")
        assert len(status) >= 4, "Status must be at least 4 characters"
        assert status[:3].isdigit(), "Status message must begin w/3-digit code"
        assert status[3] == " ", "Status message must have a space after code"

        if __debug__:
            for name, val in headers:
                name = self._convert_string_type(name, "Header name")
                val = self._convert_string_type(val, "Header value")
                # removed hop by hop headers check otherwise it raises AssertionError for Upgrade and Connection headers
                # assert not is_hop_by_hop(
                #    name
                # ), "Hop-by-hop header, '{}: {}', not allowed".format(name, val)

        self.send_headers()
        return self.write


class FixedHandler(WSGIRequestHandler):  # fixed request handler
    def address_string(self):  # Prevent reverse DNS lookups please.
        return self.client_address[0]

    def log_request(self, *args, **kw):
        try:
            if not getattr(self, "quit", False):
                return WSGIRequestHandler.log_request(self, *args, **kw)
        except:
            pass

    def get_app(self):
        return self.server.get_app()

    def handle(self):  # to add FixedServerHandler we had to override entire method
        """Handle a single HTTP request"""

        self.raw_requestline = self.rfile.readline(65537)
        if len(self.raw_requestline) > 65536:
            self.requestline = ""
            self.request_version = ""
            self.command = ""
            self.send_error(414)
            return

        if not self.parse_request():  # An error code has been sent, just exit
            return

        handler = FixedServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ()
        )
        handler.request_handler = self  # backpointer for logging
        handler.run(self.get_app())


class WebSocket(object):
    """
    Base class for supporting websocket operations.
    """

    origin = None
    protocol = None
    version = None
    path = None
    logger = logger

    def __init__(self, environ, read, write, handler, do_compress):
        self.environ = environ
        self.closed = False
        self.write = write
        self.read = read
        self.handler = handler
        self.do_compress = do_compress
        self.origin = self.environ.get("HTTP_ORIGIN")
        self.protocol = self.environ.get("HTTP_SEC_WEBSOCKET_PROTOCOL")
        self.version = self.environ.get("HTTP_SEC_WEBSOCKET_VERSION")
        self.path = self.environ.get("PATH_INFO")
        if do_compress:
            self.compressor = zlib.compressobj(7, zlib.DEFLATED, -zlib.MAX_WBITS)
            self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)

    def __del__(self):
        try:
            self.close()
        except:
            # close() may fail if __init__ didn't complete
            pass

    def _decode_bytes(self, bytestring):
        if not bytestring:
            return ""

        try:
            return bytestring.decode("utf-8")

        except UnicodeDecodeError as e:
            self.close(1007, str(e))
            raise

    def _encode_bytes(self, text):
        if not isinstance(text, str):
            text = text_type(text or "")

        return text.encode("utf-8")

    def _is_valid_close_code(self, code):
        # valid hybi close code?
        if (
            code < 1000
            or 1004 <= code <= 1006
            or 1012 <= code <= 1016
            or code
            == 1100  # not sure about this one but the autobahn fuzzer requires it.
            or 2000 <= code <= 2999
        ):
            return False

        return True

    def handle_close(self, payload):
        if not payload:
            self.close(1000, "")
            return

        if len(payload) < 2:
            raise ProtocolError("Invalid close frame: %s" % payload)

        code = struct.unpack("!H", payload[:2])[0]
        payload = payload[2:]
        if payload:
            payload.decode("utf-8")

        if not self._is_valid_close_code(code):
            raise ProtocolError("Invalid close code %s" % code)

        self.close(code, payload)

    def handle_ping(self, payload):
        self.send_frame(payload, self.OPCODE_PONG)

    def handle_pong(self, payload):
        pass

    def mask_payload(self, mask, length, payload):
        payload = bytearray(payload)
        mask = bytearray(mask)
        for i in range_type(length):
            payload[i] ^= mask[i % 4]

        return payload

    def read_message(self):
        opcode = None
        message = bytearray()

        while True:
            data = self.read(2)

            if len(data) != 2:
                first_byte, second_byte = 0, 0

            else:
                first_byte, second_byte = struct.unpack("!BB", data)

            fin = first_byte & FIN_MASK
            f_opcode = first_byte & OPCODE_MASK
            flags = first_byte & HEADER_FLAG_MASK
            length = second_byte & LENGTH_MASK
            has_mask = second_byte & MASK_MASK == MASK_MASK

            if f_opcode > 0x07:
                if not fin:
                    raise ProtocolError(
                        "Received fragmented control frame: {0!r}".format(data)
                    )
                # Control frames MUST have a payload length of 125 bytes or less
                if length > 125:
                    raise FrameTooLargeException(
                        "Control frame cannot be larger than 125 bytes: "
                        "{0!r}".format(data)
                    )

            if length == 126:
                # 16 bit length
                data = self.read(2)
                if len(data) != 2:
                    raise WebSocketError("Unexpected EOF while decoding header")
                length = struct.unpack("!H", data)[0]

            elif length == 127:
                # 64 bit length
                data = self.read(8)
                if len(data) != 8:
                    raise WebSocketError("Unexpected EOF while decoding header")
                length = struct.unpack("!Q", data)[0]

            if has_mask:
                mask = self.read(4)
                if len(mask) != 4:
                    raise WebSocketError("Unexpected EOF while decoding header")

            if self.do_compress and (flags & RSV0_MASK):
                flags &= ~RSV0_MASK
                compressed = True

            else:
                compressed = False

            if flags:
                raise ProtocolError

            if not length:
                payload = b""

            else:
                try:
                    payload = self.read(length)

                except socket.error:
                    payload = b""

                except Exception:
                    raise WebSocketError("Could not read payload")

                if len(payload) != length:
                    raise WebSocketError("Unexpected EOF reading frame payload")

                if mask:
                    payload = self.mask_payload(mask, length, payload)

                if compressed:
                    payload = b"".join(
                        (
                            self.decompressor.decompress(bytes(payload)),
                            self.decompressor.decompress(b"\0\0\xff\xff"),
                            self.decompressor.flush(),
                        )
                    )

            if f_opcode in (OPCODE_TEXT, OPCODE_BINARY):
                # a new frame
                if opcode:
                    raise ProtocolError(
                        "The opcode in non-fin frame is "
                        "expected to be zero, got "
                        "{0!r}".format(f_opcode)
                    )

                opcode = f_opcode

            elif f_opcode == OPCODE_CONTINUATION:
                if not opcode:
                    raise ProtocolError("Unexpected frame with opcode=0")

            elif f_opcode == OPCODE_PING:
                self.handle_ping(payload)
                continue

            elif f_opcode == OPCODE_PONG:
                self.handle_pong(payload)
                continue

            elif f_opcode == OPCODE_CLOSE:
                self.handle_close(payload)
                return

            else:
                raise ProtocolError("Unexpected opcode={0!r}".format(f_opcode))

            if opcode == OPCODE_TEXT:
                payload.decode("utf-8")

            message += payload

            if fin:
                break

        if opcode == OPCODE_TEXT:
            return self._decode_bytes(message)

        else:
            return message

    def receive(self):
        """
        Read and return a message from the stream. If `None` is returned, then
        the socket is considered closed/errored.
        """
        if self.closed:
            self.handler.on_close(MSG_ALREADY_CLOSED)
            raise WebSocketError(MSG_ALREADY_CLOSED)

        try:
            return self.read_message()

        except UnicodeError as e:
            self.close(1007, str(e).encode())

        except ProtocolError as e:
            self.close(1002, str(e).encode())

        except socket.timeout as e:
            self.close(message=str(e))
            self.handler.on_close(MSG_CLOSED)

        except socket.error as e:
            self.close(message=str(e))
            self.handler.on_close(MSG_CLOSED)

        return None

    def encode_header(self, fin, opcode, mask, length, flags):
        first_byte = opcode
        second_byte = 0
        extra = b""
        result = bytearray()

        if fin:
            first_byte |= FIN_MASK

        if flags & RSV0_MASK:
            first_byte |= RSV0_MASK

        if flags & RSV1_MASK:
            first_byte |= RSV1_MASK

        if flags & RSV2_MASK:
            first_byte |= RSV2_MASK

        if length < 126:
            second_byte += length

        elif length <= 0xFFFF:
            second_byte += 126
            extra = struct.pack("!H", length)

        elif length <= 0xFFFFFFFFFFFFFFFF:
            second_byte += 127
            extra = struct.pack("!Q", length)

        else:
            raise FrameTooLargeException

        if mask:
            second_byte |= MASK_MASK

        result.append(first_byte)
        result.append(second_byte)
        result.extend(extra)

        if mask:
            result.extend(mask)

        return result

    def send_frame(self, message, opcode, do_compress=False):
        if self.closed:
            self.handler.on_close(MSG_ALREADY_CLOSED)
            raise WebSocketError(MSG_ALREADY_CLOSED)

        if not message:
            return

        if opcode in (OPCODE_TEXT, OPCODE_PING):
            message = self._encode_bytes(message)

        elif opcode == OPCODE_BINARY:
            message = bytes(message)

        if do_compress and self.do_compress:
            message = self.compressor.compress(message)
            message += self.compressor.flush(zlib.Z_SYNC_FLUSH)

            if message.endswith(b"\x00\x00\xff\xff"):
                message = message[:-4]

            flags = RSV0_MASK

        else:
            flags = 0

        header = self.encode_header(True, opcode, b"", len(message), flags)

        try:
            self.write(bytes(header + message))

        except socket.error:
            raise WebSocketError(MSG_SOCKET_DEAD)

    def send(self, message, binary=None, do_compress=True):
        """
        Send a frame over the websocket with message as its payload
        """

        if binary is None:
            binary = not isinstance(message, string_types)

        opcode = OPCODE_BINARY if binary else OPCODE_TEXT

        try:
            self.send_frame(message, opcode, do_compress)

        except WebSocketError:
            self.handler.on_close(MSG_SOCKET_DEAD)
            raise WebSocketError(MSG_SOCKET_DEAD)

    def close(self, code=1000, message=b""):
        """
        Close the websocket and connection, sending the specified code and
        message.  The underlying socket object is _not_ closed, that is the
        responsibility of the initiator.
        """
        if self.closed:
            self.handler.on_close(MSG_ALREADY_CLOSED)

        try:
            message = self._encode_bytes(message)
            self.send_frame(
                struct.pack("!H%ds" % len(message), code, message), opcode=OPCODE_CLOSE
            )

        except WebSocketError:
            self.logger.debug("Failed to write closing frame -> closing socket")

        finally:
            self.logger.debug("Closed WebSocket")
            self.closed = True
            self.write = None
            self.read = None
            self.environ = None


class Response(object):
    default_content_type = "text/html; charset=UTF-8"

    # Header blacklist for specific response codes
    # (rfc2616 section 10.2.3 and 10.3.5)
    bad_headers = {
        204: frozenset(("Content-Type", "Content-Length")),
        304: frozenset(
            (
                "Allow",
                "Content-Encoding",
                "Content-Language",
                "Content-Length",
                "Content-Range",
                "Content-Type",
                "Content-Md5",
                "Last-Modified",
            )
        ),
    }
    headers_sent = False

    def __init__(self, environ, start_response, app):
        self.environ = environ
        self._start_response = start_response
        self.app = app

    def process_response(self, allow_write=True):
        try:
            results = self.app(self.environ, self.start_response)

        except Exception as e:
            self.start_response()
            log = log_traceback(e)
            err = "<h1>Internal Server Error(500)</h1><p><b>%s :%s</b></p><p><samp><pre>%s</pre></samp></p><a href=\"https://github.com/Ksengine/wsocket/issues/new?%s\" target=\"blank\"><button><h3>report</h3></button></a>" % (
                type(e).__name__,
                str(e),
                log,
                urlencode({'title':type(e).__name__,'body':'```python\n'+log+'\n```'})
            )
            return [err.encode("utf-8")]

        if not allow_write:
            return []

        if isinstance(results, string_types):
            return [results.encode("utf-8")]

        elif isinstance(results, bytes):
            return [results]

        elif hasattr(results, "__iter__"):
            while not headers_sent:
                pass

            for result in results:
                if isinstance(result, string_types):
                    self.write(result.encode("utf-8"))

                elif isinstance(result, bytes):
                    self.write(result)

                else:
                    self.write(str(result).encode("utf-8"))

            return []

        else:
            return [str(result).encode("utf-8")]

    def start_response(self, status="200 OK", headers=[]):
        if self.headers_sent:
            return

        status = self.process_status(status)

        if isinstance(headers, dict):
            headers = list(headers.items())

        if self.code in self.bad_headers:
            bad_headers = self.bad_headers[self.code]
            headers = [h for h in headers if h[0] not in bad_headers]

        if "Content-Type" not in headers:
            headers.append(("Content-Type", self.default_content_type))

        self.write = self._start_response(status, headers)
        self.headers_sent = True
        return self.write

    def process_status(self, status):
        if isinstance(status, int):
            code, status = status, _HTTP_STATUS_LINES.get(status)

        elif " " in status:
            if "\n" in status or "\r" in status or "\0" in status:
                raise ValueError("Status line must not include control chars.")

            status = status.strip()
            code = int(status.split()[0])

        else:
            raise ValueError("String status line without a reason phrase.")

        if not 100 <= code <= 999:
            raise ValueError("Status code out of range.")

        self.code = code
        return str(status or ("%d Unknown" % code))


class Event:
    def __init__(self, default=None):
        self._items = []
        self.default = default

    def __call__(self, *args, **kwargs):
        def execute():
            for func in self._items:
                try:
                    func(*args, **kwargs)

                except Exception as e:
                    logger.exception(e)

        if not len(self._items):
            if self.default:
                t = Thread(target=self.default, args=args, kwargs=kwargs)
                t.start()
                return

            else:
                return

        t = Thread(target=execute)
        t.start()

    def clear(self):
        self._items = []

    def __add__(self, item):
        self._items.append(item)
        return self

    def __sub__(self, item):
        self._items.remove(item)
        return self

    def __iadd__(self, item):
        self._items.append(item)
        return self

    def __isub__(self, item):
        self._items.remove(item)
        return self


class WSocketApp:
    SUPPORTED_VERSIONS = ("13", "8", "7")
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    websocket_class = WebSocket
    send = None
    routes = {}

    def __init__(self, app=None, protocol=None):
        self.protocol = protocol
        self.app = app or self.wsgi
        self.onclose = Event(self.on_close)
        self.onmessage = Event(self.on_message)

    def on_close(self, message):
        print(message)

    def fake(*args, **kwargs):
        pass

    def on_message(self, message, client):
        print(repr(message))
        try:
            client.send("you said: " + message)
            sleep(2)
            client.send("you said: " + message)

        except WebSocketError:
            pass

    def route(self, r):
        def decorator(callback):
            self.routes[r] = callback
            return callback

        return decorator

    def not_found(self, environ, start_response):
        start_response(404)
        return "<h1>Page Not Found(404)</h1><p><b>%s</b></p>" % (
            environ.get("PATH_INFO") + "?" + environ.get("QUERY_STRING", "\b")
        )

    def wsgi(self, environ, start_response):
        if len(self.routes):
            for route in self.routes:
                if route == environ.get("PATH_INFO"):
                    r = Response(environ, start_response, self.routes[route])
                    return r.process_response()

                if route.endswith("*") and environ.get("PATH_INFO", "").startswith(
                    route[:-1]
                ):
                    r = Response(environ, start_response, self.routes[route])
                    return r.process_response()

            r = Response(environ, start_response, self.not_found)
            return r.process_response()

        wsock = environ.get("wsgi.websocket")
        if not wsock:
            start_response()
            return "<h1>Hello World!</h1>"
        while True:
            try:
                message = wsock.receive()
                if message:
                    self.onmessage(message, wsock)

            except WebSocketError as e:
                break

        return []

    def __call__(self, environ, start_response):
        if "wsgi.websocket" in environ or environ.get("REQUEST_METHOD", "") != "GET":
            r = Response(environ, start_response, self.app)
            return r.process_response()

        if (
            environ.get("HTTP_UPGRADE", "").lower() != "websocket"
            or "upgrade" not in environ.get("HTTP_CONNECTION", "").lower()
        ):
            r = Response(environ, start_response, self.app)
            return r.process_response()

        if "HTTP_SEC_WEBSOCKET_VERSION" not in environ:
            logger.warning("No protocol defined")
            start_response(
                "426 Upgrade Required",
                [("Sec-WebSocket-Version", ", ".join(self.SUPPORTED_VERSIONS))],
            )
            return [b"No Websocket protocol version defined"]

        version = environ.get("HTTP_SEC_WEBSOCKET_VERSION")
        if version not in self.SUPPORTED_VERSIONS:
            msg = "Unsupported WebSocket Version: %s" % version
            logger.warning(msg)
            start_response(
                "400 Bad Request",
                [("Sec-WebSocket-Version", ", ".join(self.SUPPORTED_VERSIONS))],
            )
            return [msg.encode()]

        key = environ.get("HTTP_SEC_WEBSOCKET_KEY", "").strip()
        if not key:
            msg = "Sec-WebSocket-Key header is missing/empty"
            logger.warning(msg)
            start_response("400 Bad Request", [])
            return [msg.encode()]

        try:
            key_len = len(b64decode(key))

        except TypeError:
            msg = "Invalid key: %s" % key
            logger.warning(msg)
            start_response("400 Bad Request", [])
            return [msg.encode()]

        if key_len != 16:
            msg = "Invalid key: %s" % key
            logger.warning(msg)
            start_response("400 Bad Request", [])
            return [msg.encode]

        requested_protocols = environ.get("HTTP_SEC_WEBSOCKET_PROTOCOL", "")
        protocol = None
        if self.protocol and self.protocol in requested_protocols:
            protocol = self.protocol
            logger.debug("Protocol allowed: {0}".format(protocol))

        extensions = environ.get("HTTP_SEC_WEBSOCKET_EXTENSIONS")
        if extensions:
            extensions = {
                extension.split(";")[0].strip() for extension in extensions.split(",")
            }
            do_compress = "permessage-deflate" in extensions

        else:
            do_compress = False

        if PY3:
            accept = b64encode(
                sha1((key + self.GUID).encode("latin-1")).digest()
            ).decode("latin-1")

        else:
            accept = b64encode(sha1(key + self.GUID).digest())

        headers = [
            ("Upgrade", "websocket"),
            ("Connection", "Upgrade"),
            ("Sec-WebSocket-Accept", accept),
        ]

        if do_compress:
            headers.append(("Sec-WebSocket-Extensions", "permessage-deflate"))

        if protocol:
            headers.append(("Sec-WebSocket-Protocol", protocol))

        logger.debug("WebSocket request accepted, switching protocols")
        write = start_response("101 Switching Protocols", headers)
        read = environ["wsgi.input"].read
        write(b"")
        websocket = self.websocket_class(environ, read, write, self, do_compress)
        environ.update({"wsgi.websocket_version": version, "wsgi.websocket": websocket})
        r = Response(environ, start_response, self.app)
        r.start_response = self.fake
        return r.process_response(False)


# for version compat
class WebSocketHandler(FixedHandler):
    def get_app(self):
        return WSocketApp(self.server.get_app())


def run(app=WSocketApp(), host="127.0.0.1", port=8080, **options):
    handler_cls = options.get("handler_class", FixedHandler)
    server_cls = options.get("server_class", ThreadingWSGIServer)

    if ":" in host:  # Fix wsgiref for IPv6 addresses.
        if getattr(server_cls, "address_family") == socket.AF_INET:

            class server_cls(server_cls):
                address_family = socket.AF_INET6

    srv = make_server(host, port, app, server_cls, handler_cls)
    port = srv.server_port  # update port actual port (0 means random)
    print("Server started at http://%s/%i." % (host, port))
    try:
        srv.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped.")
        srv.server_close()  # Prevent ResourceWarning: unclosed socket


if __name__ == "__main__":
    run()
