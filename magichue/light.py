from abc import ABCMeta, abstractmethod
from datetime import datetime
import struct
import socket
import select
import colorsys
import logging

from .commands import Command, TurnON, TurnOFF, QueryStatus, QueryCurrentTime
from .exceptions import (
    InvalidData,
    DeviceOffline,
    DeviceDisconnected,
)

from .magichue import Status
from . import modes
from . import bulb_types
from . import utils


_LOGGER = logging.getLogger(__name__)


class AbstractLight(metaclass=ABCMeta):
    """An abstract class of MagicHue Light."""

    _LOGGER = logging.getLogger(__name__ + ".AbstractLight")

    status: Status
    allow_fading: bool = True

    def __repr__(self):
        on = "on" if self.status.on else "off"
        class_name = self.__class__.__name__
        if self.status.mode.value != modes._NORMAL:
            return "<%s: %s (%s)>" % (class_name, on, self.status.mode.name)
        else:
            if self.status.bulb_type == bulb_types.BULB_RGBWW:
                return "<{}: {} (r:{} g:{} b:{} w:{})>".format(
                    class_name,
                    on,
                    *(self.status.rgb()),
                    self.status.w,
                )
            if self.status.bulb_type == bulb_types.BULB_RGBWWCW:
                return "<{}: {} (r:{} g:{} b:{} w:{} cw:{})>".format(
                    class_name,
                    on,
                    *(self.status.rgb()),
                    self.status.w,
                    self.status.cw,
                )
            if self.status.bulb_type == bulb_types.BULB_TAPE:
                return "<{}: {} (r:{} g:{} b:{})>".format(
                    class_name,
                    on,
                    *(self.status.rgb()),
                )

    @property
    def on(self):
        return self.status.on

    @on.setter
    def on(self, value):
        if not isinstance(value, bool):
            raise ValueError("Invalid value: Should be True or False")
        if value:
            self.status.on = True
            return self.turn_on()
        else:
            self.status.on = False
            return self.turn_off()

    @property
    def rgb(self):
        return self.status.rgb()

    @rgb.setter
    def rgb(self, rgb):
        self.status.update_rgb(rgb)
        self._apply_status()

    @property
    def r(self):
        return self.status.r

    @r.setter
    def r(self, v):
        self.status.update_r(v)
        self._apply_status()

    @property
    def g(self):
        return self.status.g

    @g.setter
    def g(self, v):
        self.status.update_g(v)
        self._apply_status()

    @property
    def b(self):
        return self.status.b

    @b.setter
    def b(self, v):
        self.status.update_b(v)
        self._apply_status()

    @property
    def w(self):
        return self.status.w

    @w.setter
    def w(self, v):
        self.status.update_w(v)
        self._apply_status()

    @property
    def cw(self):
        return self.status.cw

    @cw.setter
    def cw(self, v):
        self.status.update_cw(v)
        self._apply_status()

    @property
    def cww(self):
        return (self.status.cw, self.status.w)

    @cww.setter
    def cww(self, cww):
        cw, w = cww
        self.status.update_cw(cw)
        self.status.update_w(w)
        self._apply_status()

    @property
    def is_white(self):
        return self.status.is_white

    @is_white.setter
    def is_white(self, v):
        if not isinstance(v, bool):
            raise ValueError("Invalid value: value must be a bool.")
        self.status.is_white = v
        self._apply_status()

    @property
    def hue(self):
        h = colorsys.rgb_to_hsv(*self.status.rgb())[0]
        return h

    @hue.setter
    def hue(self, h):
        if not h <= 1:
            raise ValueError("arg must not be more than 1")
        sb = colorsys.rgb_to_hsv(*self.status.rgb())[1:]
        rgb = map(int, colorsys.hsv_to_rgb(h, *sb))
        self.status.update_rgb(rgb)
        self._apply_status()

    @property
    def saturation(self):
        s = colorsys.rgb_to_hsv(*self.status.rgb())[1]
        return s

    @saturation.setter
    def saturation(self, s):
        if not s <= 1:
            raise ValueError("arg must not be more than 1")
        h, v = colorsys.rgb_to_hsv(*self.status.rgb())[::2]
        rgb = map(int, colorsys.hsv_to_rgb(h, s, v))
        self.status.update_rgb(rgb)
        self._apply_status()

    @property
    def brightness(self):
        if self.is_white:
            b = self.w
        else:
            b = colorsys.rgb_to_hsv(*self.status.rgb())[2]
        return b

    @brightness.setter
    def brightness(self, v):
        if self.is_white:
            self.status.update_w(v)
        else:
            hs = colorsys.rgb_to_hsv(*self.status.rgb())[:2]
            rgb = map(int, colorsys.hsv_to_rgb(hs[0], hs[1], v))
            self.status.update_rgb(rgb)
        self._apply_status()

    @property
    def speed(self):
        return self.status.speed

    @speed.setter
    def speed(self, value):
        value = utils.round_value(value, 0, 1)
        self.status.speed = value
        self.mode.speed = value
        self._set_mode(self.mode)

    @property
    def mode(self):
        return self.status.mode

    @mode.setter
    def mode(self, v):
        if not isinstance(v, modes.Mode):
            raise ValueError("Invalid value: value must be a instance of Mode")
        if isinstance(v, modes.CustomMode):
            self.status.speed = v.speed
        self.status.mode = v
        self._set_mode(v)

    @abstractmethod
    def _send_command(self, cmd: Command, send_only: bool = True):
        pass

    def _set_mode(self, _mode):
        self._LOGGER.debug("_set_mode")
        cmd = Command.from_array(_mode._make_data())
        self._send_command(cmd)

    def _get_status_data(self):
        self._LOGGER.debug("_get_status_data")
        data = self._send_command(QueryStatus, send_only=False)
        return data

    def get_current_time(self) -> datetime:
        """Get bulb clock time."""
        self._LOGGER.debug("get_current_time")

        data = self._send_command(QueryCurrentTime, send_only=False)
        bulb_date = datetime(
            data[3] + 2000,  # Year
            data[4],  # Month
            data[5],  # Date
            data[6],  # Hour
            data[7],  # Minute
            data[8],  # Second
        )
        return bulb_date

    def turn_on(self):
        """Trun bulb power on"""
        self._LOGGER.debug("turn_on")
        self._send_command(TurnON)
        self.status.on = True

    def turn_off(self):
        """Trun bulb power off"""
        self._LOGGER.debug("turn_off")
        self._send_command(TurnOFF)
        self.status.on = False

    def update_status(self):
        """Sync local status with bulb"""
        self._update_status()

    def _update_status(self):
        data = self._get_status_data()
        self.status.parse(data)

    def _apply_status(self):
        self._LOGGER.debug("_apply_status")
        data = self.status.make_data()
        if not self.allow_fading:
            self._LOGGER.debug("allow_fading is False")
            c = modes.CustomMode(mode=modes.MODE_JUMP, speed=0.1, colors=[self.rgb])
            self._set_mode(c)
        cmd = Command.from_array(data)
        self._send_command(cmd)


class RemoteLight(AbstractLight):

    _LOGGER = logging.getLogger(__name__ + ".RemoteLight")

    def __init__(self, api, macaddr: str, allow_fading: bool = True):
        self.api = api
        self.macaddr = macaddr
        self.status = Status()
        self.allow_fading = allow_fading
        self._update_status()

    def _send_command(self, cmd: Command, send_only: bool = True):
        self._LOGGER.debug(
            "Sending command({}) to: {}".format(
                cmd.__name__,
                self.macaddr,
            )
        )
        if send_only:
            return self.api._send_command(cmd, self.macaddr)
        else:
            data = self.str2hexarray(self._send_request(cmd))
            if len(data) != cmd.response_len:
                raise InvalidData(
                    "Expect length: %d, got %d\n%s"
                    % (cmd.response_len, len(data), str(data))
                )
            return data

    def _send_request(self, cmd: Command):
        return self.api._send_request(cmd, self.macaddr)

    @staticmethod
    def str2hexarray(hexstr: str) -> tuple:
        ls = [int(hexstr[i : i + 2], 16) for i in range(0, len(hexstr), 2)]
        return tuple(ls)


class LocalLight(AbstractLight):

    _LOGGER = logging.getLogger(__name__ + ".LocalLight")

    port = 5577
    timeout = 1

    def __init__(self, ipaddr: str, allow_fading: bool = True):
        self.ipaddr = ipaddr
        self._connect()
        self.status = Status()
        self.allow_fading = allow_fading
        self._update_status()

    def _connect(self):
        self._LOGGER.debug("Trying to make a connection with bulb(%s)" % self.ipaddr)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout)
        self._sock.connect((self.ipaddr, self.port))
        self._LOGGER.debug("Connection has been established with %s" % self.ipaddr)

    def _send(self, data):
        self._LOGGER.debug("Trying to send data(%s) to %s" % (str(data), self.ipaddr))
        if self._sock._closed:
            raise DeviceDisconnected
        self._sock.send(data)

    def _receive(self, length):
        self._LOGGER.debug(
            "Trying to receive %d bytes data from %s" % (length, self.ipaddr)
        )
        if self._sock._closed:
            raise DeviceDisconnected

        data = self._sock.recv(length)
        self._LOGGER.debug("Got %d bytes data from %s" % (len(data), self.ipaddr))
        self._LOGGER.debug("Received data: %s" % str(data))
        return data

    def _flush_receive_buffer(self):
        self._LOGGER.debug("Flushing receive buffer")
        if self._sock._closed:
            raise DeviceDisconnected
        while True:
            read_sock, _, _ = select.select([self._sock], [], [], self.timeout)
            if not read_sock:
                self._LOGGER.debug("Nothing received. buffer has been flushed")
                break
            self._LOGGER.debug("There is stil something in the buffer")
            _ = self._receive(255)
            if not _:
                raise DeviceDisconnected

    def _send_command(self, cmd: Command, send_only: bool = True):
        self._LOGGER.debug(
            "Sending command({}) to {}: {}".format(
                cmd.__name__,
                self.ipaddr,
                cmd.byte_string(),
            )
        )
        if send_only:
            self._send(cmd.byte_string())
        else:
            self._flush_receive_buffer()
            self._send(cmd.byte_string())
            data = self._receive(cmd.response_len)
            decoded_data = struct.unpack("!%dB" % len(data), data)
            if len(data) == cmd.response_len:
                return decoded_data
            else:
                raise InvalidData(
                    "Expect length: %d, got %d\n%s"
                    % (cmd.response_len, len(decoded_data), str(decoded_data))
                )

    def _connect(self, timeout=3):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((self.ipaddr, self.port))
