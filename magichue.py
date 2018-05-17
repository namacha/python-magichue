import socket
import struct


PORT =  5577


class Light:

    def __init__(self, addr):
        self.addr = addr
        self.port = 5577
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

    def _send_with_checksum(self, data):
        data_with_checksum = self._attach_checksum(data)
        self._send(struct.pack('!BBBB', *data_with_checksum))
        response = self._receive(4)
        return response

    def _turn_on(self):
        on_data = [0x71, 0x23, 0x0f]
        return self._send_with_checksum(on_data)

    def _turn_off(self):
        off_data = [0x71, 0x24, 0x0f]
        return self._send_with_checksum(off_data)

    @classmethod
    def _attach_checksum(cls, arr):
        checksum = sum(arr)
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
