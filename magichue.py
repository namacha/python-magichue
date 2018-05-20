import socket
import struct


PORT =  5577



class Color:

    SET_COLOR = 0x31

    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0
        self.w = 0  # brightness of warm white light
        self.is_white = False  # use warm white light

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
        return [self.SET_COLOR, self.r, self.g, self.b, self.w, is_white, 0x0f]  # 0x0f is a terminator


class Light:

    def __init__(self, addr, port=PORT):
        self.addr = addr
        self.port = port
        self._name = None
        self._on = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()

    def _connect(self):
        self.sock.connect((self.addr, self.port))

    def _send(self, data):
        return self.sock.send(data)

    def _receive(self, length):
        return self.sock.recv(length)

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

    @classmethod
    def _attach_checksum(cls, arr):
        hex_checksum = hex(sum(arr))
        checksum = int(hex_checksum[-2:], 16)
        return arr + [checksum]

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
