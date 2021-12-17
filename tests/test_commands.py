'''
Test: magichue/commands.py
'''

import pytest

from magichue import commands


class TestCommand(commands.Command):
    array = [0x1, 0x2, 0x3, 0xf, 0xa]
    response_length = 4


def test_cmd_hex_array():
    assert TestCommand.hex_array() == [0x1, 0x2, 0x3, 0xf, 0xa, 0x0f, 0x2e]


def test_cmd_byte_string():
    assert TestCommand.byte_string() == b'\x01\x02\x03\x0f\n\x0f\x2e'


def test_cmd_hex_string():
    assert TestCommand.hex_string() == "0102030f0a0f2e"


def test_turn_on_1():
    assert commands.TurnON.hex_array() == [0x71, 0x23, 0x0f, 0xa3]


def test_turn_on_remote():
    assert commands.TurnON.hex_array(is_remote=True) == [0x71, 0x23, 0xf0, 0x84]


def test_from_array():
    arr = [0x31, 0xa1, 0xf0, 0x12]
    cmd = commands.Command.from_array(arr)
    assert cmd.hex_string() == "31a1f0120fe3"
    assert cmd.hex_array() == arr + [0x0f, 0xe3]
