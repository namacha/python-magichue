import socket
import select
import struct
import colorsys


PORT = 5577


class Color:
    """ A Class represents color of light and its data. """

    SET_COLOR = 0x31

    def __init__(self, r=255, g=255, b=255, w=255, is_white=False):
        self.r = r
        self.g = g
        self.b = b
        self.w = w  # brightness of warm white light
        self.is_white = is_white  # use warm white light

    @staticmethod
    def color2rgb(code):
        """ color2rgb('#0F232B')  # => (15, 35, 43)"""
        if len(code) != 7:
            raise ValueError
        if code[0] != '#':
            raise ValueError
        code = code[1:]
        r = int(code[0:2], 16)
        g = int(code[2:4], 16)
        b = int(code[4:], 16)
        return r, g, b

    def make_data(self):
        is_white = 0x0f if self.is_white else 0xf0
        data = [
            self.SET_COLOR,
            self.r,
            self.g,
            self.b,
            self.w,
            is_white,
            0x0f  # 0x0f is a terminator
        ]  
        return data


class Status:

    TRUE = 0x0f
    FALSE = 0xf0
    ON = 0x23
    OFF = 0x24
    QUERY_STATUS = [0x81, 0x8a, 0x8b], 14

    def __init__(self, data):
        self.on = None
        self.color = Color()
        self.parse(data)

    def parse(self, data):
        if data[0] != 0x81:
            return
        self.on = True if data[2] == self.ON else False
        is_white = True if data[12] == self.TRUE else False
        self.color = Color(*data[6:10], is_white)


class Light:

    def __init__(self, addr, port=PORT):
        self.addr = addr
        self.port = port

        self.r = None
        self.g = None
        self.b = None
        self.w = None
        self.hue = None
        self.saturate = None
        self.brightness = None
        self.is_white = False

        self._name = None
        self._on = False
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()

    def _connect(self):
        self._sock.connect((self.addr, self.port))

    def _send(self, data):
        return self._sock.send(data)

    def _receive(self, length):
        return self._sock.recv(length)

    def _send_with_checksum(self, data, response_len):
        data_with_checksum = self._attach_checksum(data)
        self._send(struct.pack('!%dB' % len(data_with_checksum), *data_with_checksum))
        response = self._receive(response_len)
        return response

    def _turn_on(self):
        on_data = [0x71, 0x23, 0x0f]
        return self._send_with_checksum(on_data, 4)

    def _turn_off(self):
        off_data = [0x71, 0x24, 0x0f]
        return self._send_with_checksum(off_data, 4)

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
        cmd, return_len = Status.QUERY_STATUS
        raw_data = self._send_with_checksum(cmd, return_len)
        data = struct.unpack('!%dB' % return_len, raw_data)
        return data

    def _update_status(self):
        data = self._get_status_data()
        status = Status(data)
        color = status.color
        self._on = status.on
        self.r = color.r
        self.g = color.g
        self.b = color.b
        self.w = color.w
        self.is_white = color.is_white

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, value):
        if not isinstance(value, bool):
            raise ValueError('Should be True or False')
        if value:
            self._on = True
            return self._turn_on()
        else:
            self._on = False
            return self._turn_off()

    @on.deleter
    def on(self):
        pass
