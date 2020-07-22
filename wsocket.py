#!/usr/bin/python
# -*- coding: utf-8 -*-

"""# WSocket
**HTTP and Websocket both supported server(WSGI)**

Server(WSGI) creates and listens at the HTTP
socket, dispatching the requests to a handler. 
this is only use standard python libraries. 
also: 
this is a plugin to ServerLight Framework.
"""

from __future__ import print_function
try:
    from sl.server import WSGIRequestHandler
except ImportError:
    from wsgiref.simple_server import WSGIRequestHandler
import sys
import struct
from base64 import b64encode
from hashlib import sha1
import logging
from socket import error as SocketError
import errno
logger = logging.getLogger(__name__)
logging.basicConfig()
__all__ = ['WebSocketHandler']
__version__ = '1.0.0'

FIN = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE_CONN = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA


class WebSocketHandler(WSGIRequestHandler):

    """Simple HTTP and WebSocket Handler.

    This can communicate through websocket using wsgi framework. And 
    handle HTTP requests with wsgi framework as normal server.

    Automatically upgrades the connection to a websocket.
    """
    ws=False
    SUPPORTED_VERSIONS = ('13', '8', '7')
    def get_environ(self):
        """
        Add websocket to WSGI environment.
        """
        env = WSGIRequestHandler.get_environ(self)
        if self.ws:
            env['wsgi.websocket_version'] = \
                env.get('HTTP_SEC_WEBSOCKET_VERSION')
            env['wsgi.websocket'] = self
        return env
        
    def upgrade(self):
        """
        Attempt to upgrade the current environ into a websocket enabled
        connection.
        """
        
        self.env = self.get_environ()
        
        # Some basic sanity checks first
        
        logger.debug('Validating request')
        
        upgrade = self.env.get('HTTP_UPGRADE', '').lower()
        
        if upgrade == 'websocket':
            connection = self.env.get('HTTP_CONNECTION', '').lower()
            
            if 'upgrade' not in connection:
                # This is not a websocket request, so we must not handle it
                logger.warning('Client didn\'t ask for a connection upgrade')
                raise Exception('Client didn\'t ask for a connection upgrade')

        else:
            # This is not a websocket request, so we must not handle it
            return
        
        if self.request_version != 'HTTP/1.1':
            self.send_response(402, 'Bad Request')
            logger.warning('Bad server protocol in headers')
            self.wfile.write(encode_to_UTF8('Bad protocol version'))
            
            raise Exception('Bad server protocol in headers')
        
        if self.env.get('HTTP_SEC_WEBSOCKET_VERSION'):
            
            logger.debug('Attempting to upgrade connection')
            
            version = self.env.get('HTTP_SEC_WEBSOCKET_VERSION')
            
            if version not in self.SUPPORTED_VERSIONS:
                msg = 'Unsupported WebSocket Version: {0}'.format(version)
                
                logger.warning(msg)
                
                self.send_response(400, 'Bad Request')
                self.send_header('Sec-WebSocket-Version',
                        ', '.join(self.SUPPORTED_VERSIONS))
                self.end_headers()
                    
                self.wfile.write(encode_to_UTF8(msg))
                
                raise Exception(msg)

            self.ws=True
            self.handshake()
            
            self.env['wsgi.websocket_version'] = version
            self.env['wsgi.websocket'] = self
            
            return True
            
        else:
            logger.warning('No protocol defined')
            self.send_response(426, 'Upgrade Required')
            self.send_header('Sec-WebSocket-Version',
                    ', '.join(self.SUPPORTED_VERSIONS))
            self.end_headers()
            self.wfile.write(encode_to_UTF8('No Websocket protocol version defined'))
            
            raise Exception('No protocol defined')

    def handshake(self):
        
        key = self.env.get('HTTP_SEC_WEBSOCKET_KEY', '').strip()
        
        if not key:
            # 5.2.1 (3)
            msg = 'Sec-WebSocket-Key header is missing/empty'

            logger.warning(msg)
            self.send_response(400, 'Bad Request')
            
            self.wfile.write(encode_to_UTF8(msg))

        extensions = self.env.get('HTTP_SEC_WEBSOCKET_EXTENSIONS')
        if extensions:
            extensions = {extension.split(";")[0].strip() for extension in extensions.split(",")}
            do_compress = "permessage-deflate" in extensions
        else:
            do_compress = False

        logger.debug('WebSocket request accepted, switching protocols')
        self.send_response(101, 'Switching Protocols')
        self.send_header('Upgrade', 'websocket')
        self.send_header('Connection', 'Upgrade')
        self.send_header('Sec-WebSocket-Accept',
                         self.calculate_response_key(key))
        self.end_headers()
        self.keep_alive=True

    @classmethod
    def calculate_response_key(cls, key):
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        hash = sha1(key.encode() + GUID.encode())
        response_key = b64encode(hash.digest()).strip()
        return response_key.decode('ASCII')

    def receive(self):
        if not self.keep_alive:
            raise Exception('client closed connection')
        try:
            (b1, b2) = self.read_bytes(0x2)
        except SocketError as e:
            if e.errno == errno.ECONNRESET:
                logger.debug('Client closed connection.')
                self.keep_alive = 0
                return
            (b1, b2) = (0x0, 0x0)
        except ValueError as e:
            (b1, b2) = (0x0, 0x0)

        fin = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if opcode == OPCODE_CLOSE_CONN:
            logger.debug('Client asked to close connection.')
            self.keep_alive = 0
            return
        if not masked:
            logger.debug('Client must always be masked.')
            self.keep_alive = 0
            return
        if opcode == OPCODE_CONTINUATION:
            logger.debug('Continuation frames are not supported.')
            return
        elif opcode == OPCODE_BINARY:
            logger.debug('Binary frames are not supported.')
            return
        elif opcode == OPCODE_TEXT:
            opcode_handler = self._message_received_
        elif opcode == OPCODE_PING:
            opcode_handler = self.send_pong
        elif opcode == OPCODE_PONG:
            opcode_handler = self._pong_received_
        else:
            logger.debug('Unknown opcode %#x.' % opcode)
            self.keep_alive = 0
            return

        if payload_length == 0x7e:
            payload_length = struct.unpack('>H',
                    self.rfile.read(0x2))[0x0]
        elif payload_length == 0x7f:
            payload_length = struct.unpack('>Q',
                    self.rfile.read(0x8))[0x0]

        masks = self.read_bytes(4)
        message_bytes = bytearray()
        for message_byte in self.read_bytes(payload_length):
            message_byte ^= masks[len(message_bytes) % 4]
            message_bytes.append(message_byte)
        return opcode_handler(message_bytes.decode('utf8'))

    def _message_received_(self, msg):
        return msg

    def send_pong(self, msg):
        self.send(message, OPCODE_PONG)
        return

    def fake(self, *args, **kwargs):
        pass

    def _pong_received_(self, msg):
        return

    def read_bytes(self, num):

        # python3 gives ordinal of byte directly

        bytes = self.rfile.read(num)
        if sys.version_info[0x0] < 3:
            return map(ord, bytes)
        else:
            return bytes

    def send(self, message, opcode=OPCODE_TEXT):
        """
        Important: Fragmented(=continuation) messages are not supported since
        their usage cases are limited - when we don't know the payload length.
        """

        # Validate message

        if isinstance(message, bytes):
            message = try_decode_UTF8(message)  # this is slower but ensures we have UTF-8
            if not message:
                logger.debug('Can\'t send message, message is not valid UTF-8')
                return False
        elif sys.version_info < (3, 0x0) and (isinstance(message, str)
                or isinstance(message, unicode)):
            pass
        elif isinstance(message, str):
            pass
        else:
            logger.debug('Can\'t send message, message has to be a string or bytes. Given type is %s'
                            % type(message))
            return False

        header = bytearray()
        payload = encode_to_UTF8(message)
        payload_length = len(payload)

        # Normal payload

        if payload_length <= 125:
            header.append(FIN | opcode)
            header.append(payload_length)
        elif payload_length >= 0x7e and payload_length <= 65535:

        # Extended payload

            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT16)
            header.extend(struct.pack('>H', payload_length))
        elif payload_length < 18446744073709551616:

        # Huge extended payload

            header.append(FIN | opcode)
            header.append(PAYLOAD_LEN_EXT64)
            header.extend(struct.pack('>Q', payload_length))
        else:

            raise Exception('Message is too big. Consider breaking it into chunks.'
                            )
            return
        try:
            self.wfile.write(header + payload)
        except:
            raise Exception

    def do_GET(self):
        try:
            if self.upgrade():
                self.server.get_app()(self.get_environ(),self.fake)

            else:
                WSGIRequestHandler.do_GET(self)
        except:
            pass

    def do_POST(self):
        WSGIRequestHandler.do_POST(self)

    def finish_response(self):
        if hasattr(self.s.result, 'close'):
            self.s.result.close()
        self.s.close()
    
    def __del__(self):
        try:
            self.close()
        except:
            # close() may fail if __init__ didn't complete
            pass

    @property
    def current_app(self):
        return self.server.get_app()

    @property
    def origin(self):
        return self.env.get('HTTP_ORIGIN')

    @property
    def protocol(self):
        return self.env.get('HTTP_SEC_WEBSOCKET_PROTOCOL')

    @property
    def version(self):
        return self.env.get('HTTP_SEC_WEBSOCKET_VERSION')

    @property
    def logger(self):
        return logger

def encode_to_UTF8(data):
    try:
        return data.encode('UTF-8')
    except UnicodeEncodeError as e:
        logger.debug('Could not encode data to UTF-8 -- %s' % e)
        return False
    except Exception as e:
        raise e
        return False


def try_decode_UTF8(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return False
    except Exception as e:
        raise e
