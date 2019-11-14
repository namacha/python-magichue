import socket
import select
import struct
import colorsys

from . import modes
from . import bulb_types
from . import commands
from . import utils

PORT = 5577


class Status(object):

    ON = 0x23
    OFF = 0x24

    def __init__(self, r=0, g=0, b=0, w=255, is_white=True, on=True):
        self.r = r
        self.g = g
        self.b = b
        self.w = w  # brightness of warm white light
        self.is_white = is_white  # use warm white light
        self.on = on
        self.speed = 1.0  # maximum by default
        self.mode = modes.NORMAL
        self.bulb_type = bulb_types.BULB_NORMAL

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    def parse(self, data):
        if data[0] != 0x81:
            return
        self.bulb_type = data[1]
        self.on = data[2] == commands.ON
        self.is_white = data[12] == commands.TRUE
        self.r, self.g, self.b, self.w = data[6:10]
        mode_value = data[3]
        self.mode = modes._VALUE_TO_MODE[mode_value]
        slowness = data[5]
        self.speed = utils.slowness2speed(slowness)

    def make_data(self):
        is_white = 0x0f if self.is_white else 0xf0
        data = [
            commands.SET_COLOR,
            self.r,
            self.g,
            self.b,
            self.w,
            is_white,
            0x0f  # 0x0f is a terminator
        ]
        return data


class Light(object):

    PORT = 5577

    def __repr__(self):
        on = 'on' if self.on else 'off'
        if self._status.mode.value == modes._NORMAL:
            return '<Light: {} (r:{} g:{} b:{} w:{})>'.format(
                on,
                self._status.r,
                self._status.g,
                self._status.b,
                self._status.w,
            )
        else:
            return '<Light: %s (%s)>' % (on, self._status.mode.name)

    def __init__(
            self,
            addr,
            port=PORT,
            name="None",
            confirm_receive_on_send=None,
            allow_fading=True):
        self.addr = addr
        self.port = port
        self.name = name

        self.allow_fading = allow_fading

        self._status = Status()
        self._connect()
        self._update_status()

        if confirm_receive_on_send is not None:
            self.confirm_receive_on_send = confirm_receive_on_send
        else:
            self.confirm_receive_on_send =\
                self._status.bulb_type == bulb_types.BULB_NORMAL

    def _connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.addr, self.port))

    def _send(self, data):
        return self._sock.send(data)

    def _receive(self, length):
        return self._sock.recv(length)

    def _send_with_checksum(self, data, response_len, receive=True):
        data_with_checksum = self._attach_checksum(data)
        format_str = '!%dB' % len(data_with_checksum)
        data = struct.pack(format_str, *data_with_checksum)
        self._send(data)
        if receive:
            response = self._receive(response_len)
            return response

    def _turn_on(self):
        on_data = [commands.TURN_ON_1, commands.TURN_ON_2, commands.TURN_ON_3]
        return self._send_with_checksum(on_data, commands.RESPONSE_LEN_POWER, receive=self.confirm_receive_on_send)

    def _turn_off(self):
        off_data = [commands.TURN_OFF_1, commands.TURN_OFF_2, commands.TURN_OFF_3]
        return self._send_with_checksum(off_data, commands.RESPONSE_LEN_POWER, receive=self.confirm_receive_on_send)

    def _flush_receive_buffer(self, timeout=0.2):
        while True:
            read_sock, _, _ = select.select([self._sock], [], [], timeout)
            if not read_sock:
                break
            _ = self._sock.recv(255)

    def _confirm_checksum(self, received):
        data_without_checksum = received[:-1]
        calculated_checksum = self._calc_checksum(data_without_checksum)
        received_checksum = received[-1]
        return calculated_checksum == received_checksum

    def _calc_checksum(self, data):
        hex_checksum = hex(sum(data))
        checksum = int(hex_checksum[-2:], 16)
        return checksum

    def _attach_checksum(self, data):
        checksum = self._calc_checksum(data)
        return data + [checksum]

    def _get_status_data(self):
        self._flush_receive_buffer()
        cmd = [
            commands.QUERY_STATUS_1,
            commands.QUERY_STATUS_2,
            commands.QUERY_STATUS_3,
        ]

        raw_data = self._send_with_checksum(
            cmd,
            commands.RESPONSE_LEN_QUERY_STATUS,
        )
        data = struct.unpack('!%dB' % commands.RESPONSE_LEN_QUERY_STATUS, raw_data)
        return data

    def _update_status(self):
        data = self._get_status_data()
        self._status.parse(data)

    def update_status(self):
        self._update_status()

    def _apply_status(self):
        data = self._status.make_data()
        if not self.allow_fading:
            c = modes.CustomMode(
                mode=modes.MODE_JUMP,
                speed=0.1,
                colors=[(self._status.r, self._status.g, self._status.b)],
            )
            self._set_mode(c)
        self._send_with_checksum(
            data,
            commands.RESPONSE_LEN_SET_COLOR,
            receive=self.confirm_receive_on_send
        )

    @property
    def rgb(self):
        return self._status.rgb

    @rgb.setter
    def rgb(self, rgb):
        r, g, b = rgb
        if r not in range(256):
            raise ValueError("arg not in range(256)")
        if g not in range(256):
            raise ValueError("arg not in range(256)")
        if b not in range(256):
            raise ValueError("arg not in range(256)")
        self._status = Status(r, g, b, self.w, self.is_white, self.on)
        self._apply_status()

    @property
    def r(self):
        return self._status.r

    @r.setter
    def r(self, v):
        if v not in range(256):
            raise ValueError("arg not in range(256)")
        self._status.r = v
        self._apply_status()

    @property
    def g(self):
        return self._status.g

    @g.setter
    def g(self, v):
        if v not in range(256):
            raise ValueError("arg not in range(256)")
        self._status.g = v
        self._apply_status()

    @property
    def b(self):
        return self._status.b

    @b.setter
    def b(self, v):
        if v not in range(256):
            raise ValueError("arg not in range(256)")
        self._status.b = v
        self._apply_status()

    @property
    def w(self):
        return self._status.w

    @w.setter
    def w(self, v):
        if v not in range(256):
            raise ValueError("arg not in range(256)")
        self._status.w = v
        self._apply_status()

    @property
    def is_white(self):
        return self._status.is_white

    @is_white.setter
    def is_white(self, v):
        if not isinstance(v, bool):
            raise ValueError("arg not in range(256)")
        self._status.is_white = v
        self._apply_status()

    @property
    def hue(self):
        h = colorsys.rgb_to_hsv(*self._status.rgb)[0]
        return h

    @hue.setter
    def hue(self, h):
        if not h <= 1:
            raise ValueError("arg must not be more than 1")
        sb = colorsys.rgb_to_hsv(*self._status.rgb)[1:]
        rgb = map(int, colorsys.hsv_to_rgb(h, *sb))
        r, g, b = rgb
        self._status = Status(r, g, b, self.w, self.is_white, self.on)
        self._apply_status()

    @property
    def saturation(self):
        s = colorsys.rgb_to_hsv(*self._status.rgb)[1]
        return s

    @saturation.setter
    def saturation(self, s):
        if not s <= 1:
            raise ValueError("arg must not be more than 1")
        h, v = colorsys.rgb_to_hsv(*self._status.rgb)[::2]
        rgb = map(int, colorsys.hsv_to_rgb(h, s, v))
        r, g, b = rgb
        self._status = Status(r, g, b, self.w, self.is_white, self.on)
        self._apply_status()

    @property
    def brightness(self):
        if self.is_white:
            b = self.w
        else:
            b = colorsys.rgb_to_hsv(*self._status.rgb)[2]
        return b

    @brightness.setter
    def brightness(self, v):
        if v not in range(256):
            raise ValueError("arg not in range(256)")
        if self.is_white:
            r, g, b = self.rgb
            self._status = Status(r, g, b, v, self.is_white, self.on)
        else:
            hs = colorsys.rgb_to_hsv(*self._status.rgb)[:2]
            rgb = map(int, colorsys.hsv_to_rgb(hs[0], hs[1], v))
            r, g, b = rgb
            self._status = Status(r, g, b, self.w, self.is_white, self.on)
        self._apply_status()

    @property
    def speed(self):
        return self._status.speed

    @speed.setter
    def speed(self, value):
        if value >= 1:
            value = 1
        elif value < 0:
            value = 0
        self._status.speed = value
        self._set_mode(self.mode)

    @property
    def on(self):
        return self._status.on

    @on.setter
    def on(self, value):
        if not isinstance(value, bool):
            raise ValueError("Should be True or False")
        if value:
            self._status.on = True
            return self._turn_on()
        else:
            self._status.on = False
            return self._turn_off()

    @on.deleter
    def on(self):
        pass

    @property
    def mode(self):
        return self._status.mode

    @property
    def mode_str(self):
        return modes._VALUE_TO_NAME[self._status.mode]

    @mode_str.setter
    def mode_str(self, value):
        pass

    @mode.setter
    def mode(self, mode):
        if isinstance(mode, modes.Mode):
            mode.speed = self.speed
            self._set_mode(mode)

    @mode.deleter
    def mode(self):
        pass

    def _set_mode(self, mode):
        mode.speed = self.speed
        self._status.mode = mode
        self._send_with_checksum(
            mode._make_data(),
            mode.RESPONSE_LEN,
            receive=self.confirm_receive_on_send
        )
