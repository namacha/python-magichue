from abc import ABCMeta, abstractmethod
import struct
from datetime import datetime
import socket
import select
import logging

from .commands import (
    Command,
    TurnON,
    TurnOFF,
    QueryStatus,
    QueryCurrentTime
)

from .magichue import Status
from . import modes
from . import bulb_types


_LOGGER = logging.getLogger(__name__)


class InvalidData(Exception):
    pass


class AbstractLight(metaclass=ABCMeta):
    '''An abstract class of MagicHue Light.'''

    status: Status
    allow_fading: bool = False

    def __repr__(self):
        on = 'on' if self.status.on else 'off'
        class_name = self.__class__.__name__
        if self.status.mode.value != modes._NORMAL:
            return '<%s: %s (%s)>' % (class_name, on, self.status.mode.name)
        else:
            if self.status.bulb_type == bulb_types.BULB_RGBWW:
                return '<{}: {} (r:{} g:{} b:{} w:{})>'.format(
                    class_name,
                    on,
                    *(self.status.rgb()),
                    self.status.w,
                )
            if self.status.bulb_type == bulb_types.BULB_RGBWWCW:
                return '<{}: {} (r:{} g:{} b:{} w:{} cw:{})>'.format(
                    class_name,
                    on,
                    *(self.status.rgb()),
                    self.status.w,
                    self.status.cw,
                )
            if self.status.bulb_type == bulb_types.BULB_TAPE:
                return '<{}: {} (r:{} g:{} b:{})>'.format(
                    class_name,
                    on,
                    *(self.status.rgb()),
                )

    @abstractmethod
    def _send_command(self, cmd: Command, send_only: bool = True):
        pass

    @abstractmethod
    def _get_status_data(self):
        pass

    def get_current_time(self) -> datetime:
        '''Get bulb clock time.'''

        data = self._send_command(QueryCurrentTime, send_only=False)
        bulb_date = datetime(
            data[3] + 2000,  # Year
            data[4],         # Month
            data[5],         # Date
            data[6],         # Hour
            data[7],         # Minute
            data[8],         # Second
        )
        return bulb_date

    def turn_on(self):
        self._send_command(TurnON)

    def turn_off(self):
        self._send_command(TurnOFF)

    def _update_status(self):
        data = self._get_status_data()
        self.status.parse(data)

    def _apply_status(self):
        data = self.status.make_data()
        cmd = Command.from_array(data)
        self._send_command(cmd)



class RemoteLight(AbstractLight):

    _LOGGER = logging.getLogger(__name__ + '.RemoteLight')

    def __init__(self, api, macaddr: str):
        self.api = api
        self.macaddr = macaddr
        self.status = Status()

    def _send_command(self, cmd: Command, send_only: bool = True):
        self._LOGGER.debug('Sending command({}) to: {}'.format(
            cmd.__name__,
            self.macaddr,
        ))
        if send_only:
            return self.api._send_command(cmd, self.macaddr)
        else:
            data = self.str2hexarray(self._send_request(cmd))
            if len(data) != cmd.response_len:
                raise InvalidData(
                    'Expect length: %d, got %d\n%s' % (response_len, len(data), str(data))
                )
            return data

    def _send_request(self, cmd: Command):
        return self.api._send_request(cmd, self.macaddr)

    @staticmethod
    def str2hexarray(hexstr: str) -> tuple:
        return tuple([int(hexstr[i:i+2], 16) for i in range(0, len(hexstr), 2)])

    def _get_status_data(self):
        data_arr = self.api.get_devices().get('data')
        for dev in data_arr:
            if dev.get('macAddress') == self.macaddr:
                return self.str2hexarray(dev.get('state'))


class LocalLight(AbstractLight):

    _LOGGER = logging.getLogger(__name__ + '.LocalLight')

    port = 5577
    timeout = 1

    def __init__(self, ipaddr):
        self.ipaddr = ipaddr
        self._connect()
        self.status = Status()

    def _connect(self):
        self._LOGGER.debug('Trying to make a connection with bulb(%s)' % self.ipaddr)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout)
        self._sock.connect((self.ipaddr, self.port))
        self._LOGGER.debug('Connection has been established with %s' % self.ipaddr)

    def _send(self, data):
        self._sock.sendall(data)

    def _receive(self, length):
        self._LOGGER.debug('Trying to receive a data with %d bytes' % length)
        raw_data = self._sock.recv(length)
        self._LOGGER.debug('Received data: %s' % str(raw_data))
        return raw_data


    def _flush_receive_buffer(self):
        self._LOGGER.debug('Flushing receive buffer')
        while True:
            read_sock, _, _ = select.select([self._sock], [], [], self.timeout)
            if not read_sock:
                self._LOGGER.debug('Nothing received. buffer has been flushed')
                break
            self._LOGGER.debug('There is stil something in the buffer')
            _ = self._receive(255)

    def _send_command(self, cmd: Command, send_only: bool = True):
        self._LOGGER.debug('Sending command({}) to {}: {}'.format(
            cmd.__name__,
            cmd.byte_string(),
            self.ipaddr,
        ))
        if send_only:
            self._send(cmd.byte_string())
        else:
            self._flush_receive_buffer()
            self._send(cmd.byte_string())
            data = self._receive(cmd.response_len)
            decoded_data = struct.unpack(
                    '!%dB' % len(data),
                    data
            )
            if len(data) == cmd.response_len:
                return decoded_data
            else:
                raise InvalidData(
                    'Expect length: %d, got %d\n%s' % (
                        response_len,
                        len(decoded_data),
                        str(decoded_data)
                    )
                )

    def _get_status_data(self):
        data_arr = self._send_command(QueryStatus, send_only=False)
        return data_arr

    def _connect(self, timeout=3):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((self.ipaddr, self.port))

    def _send(self, data):
        self._LOGGER.debug(
            'Trying to send data(%s) to %s' % (str(data), self.ipaddr)
        )

        self._sock.send(data)

    def _receive(self, length):
        self._LOGGER.debug(
            'Trying to receive %d bytes data from %s' % (length, self.ipaddr)
        )
        data = self._sock.recv(length)
        self._LOGGER.debug(
            'Got %d bytes data from %s' % (len(data), self.ipaddr)
        )
        return data
