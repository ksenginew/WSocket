#!/usr/bin/python
# -*- coding: utf-8 -*-

"""# WSocket
**HTTP and Websocket both supported wsgi server**

WSGI Server creates and listens at the HTTP
socket, dispatching the requests to a handler.
 this is a plugin to ServerLight Framework.
"""

from __future__ import print_function
from sl import WSGIHandler
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


class WebSocketHandler(WSGIHandler):

    """Simple HTTP and WebSocket Handler.

    This can communicate through websocket using wsgi framework. And 
    handle HTTP requests with wsgi framework as normal server.

    """

    SUPPORTED_VERSIONS = ('13', '8', '7')

    def do_GET(self):
        self.env = self.get_environ()
        if 'HTTP_CONNECTION' in self.env:
            if self.env['HTTP_CONNECTION'] == 'Upgrade':
                logger.info('Connection Upgrade Requested.')
                if 'HTTP_UPGRADE' in self.env:
                    if self.env['HTTP_UPGRADE'].lower() == 'websocket':
                        logger.info('Upgrade to Websocket Requested.')
                        if self.env.get('HTTP_SEC_WEBSOCKET_VERSION'):
                            logger.info('Handshaking...')
                            self.handshake()
                            self.send(str(self.server.application(self.env,
                                    self.fake)))
                        else:
                            logger.info('Secure WebSocket Version Not Found ?'
                                    )
                            self.send_response(426, 'Upgrade Required')
                            self.send_header('Sec-WebSocket-Version',
                                    ', '.join(self.SUPPORTED_VERSIONS))
                            self.end_headers()
            else:
                logger.info("Client didn't ask for a connection upgrade"
                            )

                # It's time to call our application callable and get
                # back a result that will become HTTP response body

                result = self.server.application(self.env,
                        self.start_response)
                self.finish_response(result)

    def handshake(self):
        if self.env.get('HTTP_SEC_WEBSOCKET_VERSION') \
            not in self.SUPPORTED_VERSIONS:
            logger.info('Unsupported Secure WebSocket Version ?')
            self.send_response(404, 'Bad Request')
            self.send_header('Sec-WebSocket-Version',
                             ', '.join(self.SUPPORTED_VERSIONS))
            self.end_headers()
            return
        self.env['wsgi.websocket_version'] = \
            self.env.get('HTTP_SEC_WEBSOCKET_VERSION')
        self.env['wsgi.websocket'] = self
        try:
            key = self.env['HTTP_SEC_WEBSOCKET_KEY']
            print(key)
        except KeyError:
            logger.info('Secure WebSocket Key Not Found ?')
            self.send_response(404, 'Bad Request')
            return
        logger.info('Switching Protocols...')
        self.send_response(101, 'Switching Protocols')
        self.send_header('Upgrade', 'websocket')
        self.send_header('Connection', 'Upgrade')
        self.send_header('Sec-WebSocket-Accept',
                         self.calculate_response_key(key))
        self.end_headers()

    @classmethod
    def calculate_response_key(cls, key):
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        hash = sha1(key.encode() + GUID.encode())
        response_key = b64encode(hash.digest()).strip()
        return response_key.decode('ASCII')

    def receive(self):
        try:
            (b1, b2) = self.read_bytes(0x2)
        except SocketError as e:
            if e.errno == errno.ECONNRESET:
                logger.info('Client closed connection.')
                return
            (b1, b2) = (0x0, 0x0)
        except ValueError as e:
            (b1, b2) = (0x0, 0x0)

        fin = b1 & FIN
        opcode = b1 & OPCODE
        masked = b2 & MASKED
        payload_length = b2 & PAYLOAD_LEN

        if opcode == OPCODE_CLOSE_CONN:
            logger.info('Client asked to close connection.')
            return
        if not masked:
            logger.warn('Client must always be masked.')
            return
        if opcode == OPCODE_CONTINUATION:
            logger.warn('Continuation frames are not supported.')
            return
        elif opcode == OPCODE_BINARY:
            logger.warn('Binary frames are not supported.')
            return
        elif opcode == OPCODE_TEXT:
            opcode_handler = self._message_received_
        elif opcode == OPCODE_PING:
            opcode_handler = self.send_pong
        elif opcode == OPCODE_PONG:
            opcode_handler = self._pong_received_
        else:
            logger.warn('Unknown opcode %#x.' % opcode)
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
                logger.warning("Can\'t send message, message is not valid UTF-8"
                               )
                return False
        elif sys.version_info < (3, 0x0) and (isinstance(message, str)
                or isinstance(message, unicode)):
            pass
        elif isinstance(message, str):
            pass
        else:
            logger.warning('Can\'t send message, message has to be a string or bytes. Given type is %s'
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

        self.wfile.write(header + payload)


def encode_to_UTF8(data):
    try:
        return data.encode('UTF-8')
    except UnicodeEncodeError as e:
        logger.error('Could not encode data to UTF-8 -- %s' % e)
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
