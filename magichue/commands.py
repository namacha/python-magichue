import struct
from typing import List


class _Meta(type):
    required_attributes = ["array", "response_len"]

    def __new__(cls, classname, bases, _dict):
        newclass = type.__new__(cls, classname, bases, _dict)
        for attr_name in cls.required_attributes:
            if not hasattr(newclass, attr_name):
                raise NotImplementedError(f"{newclass.__name__}.{attr_name} is not set")
        return newclass


class Command:

    needs_terminator = True
    array: List[int]
    response_len: int

    @classmethod
    def append_terminator(cls, arr, is_remote):
        if cls.needs_terminator:
            return arr + [0xF0 if is_remote else 0x0F]
        else:
            return arr

    @staticmethod
    def calc_checksum(arr):
        hex_checksum = hex(sum(arr))[-2:]
        checksum = int(hex_checksum, 16)
        return checksum

    @classmethod
    def from_array(cls, arr, response_len: int = 0):
        cmd = Command
        cmd.array = arr
        cmd.response_len = response_len
        return cmd

    @classmethod
    def attach_checksum(cls, arr):
        return arr + [cls.calc_checksum(arr)]

    @classmethod
    def hex_array(cls, is_remote: bool = False) -> list:
        return cls.attach_checksum(cls.append_terminator(cls.array, is_remote))

    @classmethod
    def byte_string(cls, is_remote: bool = False) -> bytes:
        _arr = cls.attach_checksum(cls.append_terminator(cls.array, is_remote))
        return struct.pack("!%dB" % len(_arr), *_arr)

    @classmethod
    def hex_string(cls, is_remote: bool = False) -> str:
        _arr = cls.attach_checksum(cls.append_terminator(cls.array, is_remote))
        return "".join([hex(v)[2:].zfill(2) for v in _arr])


class TurnON(Command, metaclass=_Meta):
    """Command: Turn on light bulb.
    Response:
    (240, 113, 35, 133)
     |    |    |   |
     |    |    |   Checksum
     |    |    Status: 0x23(TurnON)
     |    Header
     Header: 0xf0(240): Remote, 0x0f(15): Local
    """

    array = [0x71, 0x23]
    response_len = 4


class TurnOFF(Command, metaclass=_Meta):
    """Command: Turn off light bulb.
    Response:
    (240, 113, 36, 133)
     |    |    |   |
     |    |    |   Checksum
     |    |    Status: 0x24(TurnOFF)
     |    Header
     Header: 0xf0(240): Remote, 0x0f(15): Local
    """

    array = [0x71, 0x24]
    response_len = 4


class QueryStatus(Command, metaclass=_Meta):
    """Command: Query status of light bulb.
    Response:
    (129, 53, 36, 97, 0, 1, 0, 0, 0, 255, 7, 0, 15, 81)
     |    |   |   |   |  |  |  |  |  |    |  |  |   |
     |    |   |   |   |  |  |  |  |  |    |  |  |   CheckSum
     |    |   |   |   |  |  |  |  |  |    |  |  Color Status: 0x0f(15) RGB, 0xf0(240) White
     |    |   |   |   |  |  |  |  |  |    |  CoolWhite(0-255)
     |    |   |   |   |  |  |  |  |  |    Version
     |    |   |   |   |  |  |  |  |  WarmWhite(0-255)
     |    |   |   |   |  |  |  |  B(0-255)
     |    |   |   |   |  |  |  G(0-255)
     |    |   |   |   |  |  R(0-255)
     |    |   |   |   |  Speed(0x1-0x1f): 0x1 is fastest
     |    |   |   |   Run/Pause
     |    |   |   Mode
     |    |   ON/OFF: 0x23(35) ON, 0x24(36) OFF
     |    Device Type
     Header
    """

    array = [0x81, 0x8A, 0x8B]
    response_len = 14
    needs_terminator = False


class QueryCurrentTime(Command, metaclass=_Meta):
    """Command: Query time of bulb clock
    Response:
    (240, 17, 20, 21, 12, 21, 17, 38, 7, 2, 0, 139)
     |    |   |   |   |   |   |   |   |  |  |  |
     |    |   |   |   |   |   |   |   |  |  |  Checksum
     |    |   |   |   |   |   |   |   |  |  Reserved
     |    |   |   |   |   |   |   |   |  Day of week
     |    |   |   |   |   |   |   |   Second
     |    |   |   |   |   |   |   Minute
     |    |   |   |   |   |   Hour
     |    |   |   |   |   Date
     |    |   |   |   Month
     |    |   |   Year
     |    |   Header
     |    Header
     Header: 0xf0(240): Remote, 0x0f(15): Local
    """

    array = [0x11, 0x1A, 0x1B]
    response_len = 12


class QueryTimers(Command, metaclass=_Meta):
    """Command: Query scheduled timers"""

    array = [0x22, 0x2A, 0x2B]
    response_len = 94


class QueryCustomMode(Command, metaclass=_Meta):
    """Query custom mode content"""

    array = [0x52, 0x5A, 0x5B]
    response_len = 70


QUERY_STATUS_1 = 0x81
QUERY_STATUS_2 = 0x8A
QUERY_STATUS_3 = 0x8B
RESPONSE_LEN_QUERY_STATUS = 14

SET_COLOR = 0x31
RESPONSE_LEN_SET_COLOR = 1

CHANGE_MODE = 0x61
RESPONSE_LEN_CHANGE_MODE = 1

CUSTOM_MODE = 0x51
RESPONSE_LEN_CUSTOM_MODE = 0

CUSTOM_MODE_TERMINATOR_1 = 0xFF
CUSTOM_MODE_TERMINATOR_2 = 0xF0

TURN_ON_1 = 0x71
TURN_ON_2 = 0x23
TURN_ON_3 = 0x0F
TURN_OFF_1 = 0x71
TURN_OFF_2 = 0x24
TURN_OFF_3 = 0x0F
RESPONSE_LEN_POWER = 4


TRUE = 0x0F
FALSE = 0xF0
ON = 0x23
OFF = 0x24
