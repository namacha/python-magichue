import struct
from typing import List


class Command:

    array: List[int]
    response_length: int

    @staticmethod
    def append_terminator(arr, is_remote):
        return arr + [0xf0 if is_remote else 0x0f]

    @staticmethod
    def calc_checksum(arr):
        hex_checksum = hex(sum(arr))[-2:]
        checksum = int(hex_checksum, 16)
        return checksum

    @classmethod
    def attach_checksum(cls, arr):
        return arr + [cls.calc_checksum(arr)]

    @classmethod
    def hex_array(cls, is_remote: bool=False):
        return cls.attach_checksum(
            cls.append_terminator(cls.array, is_remote)
        )

    @classmethod
    def byte_string(cls, is_remote: bool=False):
        _arr = cls.attach_checksum(
            cls.append_terminator(cls.array, is_remote)
        )
        return struct.pack('!%dB' % len(_arr), *_arr)

    @classmethod
    def hex_string(cls, is_remote: bool=False):
        _arr = cls.attach_checksum(
            cls.append_terminator(cls.array, is_remote)
        )
        return ''.join([hex(v)[2:].zfill(2) for v in _arr])


class TurnON(Command):
    array = [0x71, 0x23]
    response_length = 14


class TurnOFF(Command):
    array = [0x71, 0x24]
    response_length = 14


class QueryStatus(Command):
    array = [0x81, 0x8a, 0x8b]
    response_length = 14


QUERY_STATUS_1 = 0x81
QUERY_STATUS_2 = 0x8a
QUERY_STATUS_3 = 0x8b
RESPONSE_LEN_QUERY_STATUS = 14

SET_COLOR = 0x31
RESPONSE_LEN_SET_COLOR = 1

CHANGE_MODE = 0x61
RESPONSE_LEN_CHANGE_MODE = 1

CUSTOM_MODE = 0x51
RESPONSE_LEN_CUSTOM_MODE = 0

CUSTOM_MODE_TERMINATOR_1 = 0xff
CUSTOM_MODE_TERMINATOR_2 = 0xf0

TURN_ON_1 = 0x71
TURN_ON_2 = 0x23
TURN_ON_3 = 0x0f
TURN_OFF_1 = 0x71
TURN_OFF_2 = 0x24
TURN_OFF_3 = 0x0f
RESPONSE_LEN_POWER = 4


TRUE = 0x0f
FALSE = 0xf0
ON = 0x23
OFF = 0x24
