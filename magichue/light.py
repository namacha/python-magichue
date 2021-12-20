from abc import ABCMeta, abstractmethod
import struct
import socket
import logging

from .commands import (
    Command,
    TurnON,
    TurnOFF,
    QueryStatus
)

from .magichue import Status
from . import modes
from . import bulb_types


_LOGGER = logging.getLogger()


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
    def _send_command(self, cmd: Command):
        pass

    @abstractmethod
    def _get_status_data(self):
        pass

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

    def __init__(self, api, macaddr: str):
        self.api = api
        self.macaddr = macaddr
        self.status = Status()

    def _send_command(self, cmd: Command):
        #self._send_request(cmd)
        return self.api._send_command(cmd, self.macaddr)

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

    port = 5577

    def __init__(self, ipaddr):
        self.ipaddr = ipaddr
        self._connect()
        self.status = Status()

    def _connect(self, timeout=3):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((self.ipaddr, self.port))

    def _send(self, data):
        self._sock.send(data)

    def _receive(self, length):
        return self._sock.recv(length)

    def _send_command(self, cmd: Command):
        _LOGGER.debug('Sending packet: {}'.format(cmd.byte_string()))
        self._send(cmd.byte_string())

    def _get_status_data(self):
        self._send_command(QueryStatus)
        raw_data = self._sock.recv(QueryStatus.response_len)
        data_arr = struct.unpack(
            '!%dB' % QueryStatus.response_len,
            raw_data
        )
        return data_arr
