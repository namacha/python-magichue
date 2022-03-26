from .commands import (
    CHANGE_MODE,
    CUSTOM_MODE,
    CUSTOM_MODE_TERMINATOR_1,
    CUSTOM_MODE_TERMINATOR_2,
    RESPONSE_LEN_CHANGE_MODE,
    RESPONSE_LEN_CUSTOM_MODE,
)

from .utils import speed2slowness


__all__ = [
    "RAINBOW_CROSSFADE",
    "RED_GRADUALLY",
    "GREEN_GRADUALLY",
    "BLUE_GRADUALLY",
    "YELLOW_GRADUALLY",
    "BLUE_GREEN_GRADUALLY",
    "PURPLE_GRADUALLY",
    "WHITE_GRADUALLY",
    "RED_GREEN_CROSSFADE",
    "RED_BLUE_CROSSFADE",
    "GREEN_BLUE_CROSSFADE",
    "RAINBOW_STROBE",
    "RED_STROBE",
    "GREEN_STROBE",
    "BLUE_STROBE",
    "YELLOW_STROBE",
    "BLUE_GREEN_STROBE",
    "PURPLE_STROBE",
    "WHITE_STROBE",
    "RAINBOW_FLASH",
    "NORMAL",
    "MODE_GRADUALLY",
    "MODE_JUMP",
    "MODE_STROBE",
    "CUSTOM_MODE_BLANK",
    "Mode",
    "CustomMode",
    "SETUP_MODE",
]


class Mode:

    RESPONSE_LEN = RESPONSE_LEN_CHANGE_MODE

    def __repr__(self):
        return "<Mode: {}>".format(self._status_text())

    def _status_text(self):
        return self.name

    def __init__(self, value, speed, name):
        self.value = value
        self.speed = speed
        self.name = name

    def _make_data(self):  # slowness is a integer value 1 to 49
        slowness = speed2slowness(self.speed)
        d = [CHANGE_MODE, self.value, slowness]
        return d


class CustomMode(Mode):

    RESPONSE_LEN = RESPONSE_LEN_CUSTOM_MODE

    def __repr__(self):
        return "<CustomMode: {} colors, speed={}, mode={}>".format(
            len(self.colors),
            self.speed,
            self.name,
        )

    def __init__(self, mode, speed, colors):
        super().__init__(CUSTOM, speed, "CUSTOM")
        self.colors = colors
        self.speed = speed
        self.mode = mode
        self._color_list = self._make_colors_list()

    def _trim_colors_list(self):
        blank_colors = [CUSTOM_MODE_BLANK]
        if len(self.colors) < 16:
            diff = 16 - len(self.colors)
            return self.colors + blank_colors * diff
        if len(self.colors) >= 16:
            return self.colors[:16]

    def _make_colors_list(self):
        ls = []
        colors = self._trim_colors_list()
        for r, g, b in colors:
            ls.append(r)
            ls.append(g)
            ls.append(b)
            ls.append(0)
        return ls

    def _make_data(self):
        data = (
            [CUSTOM_MODE]
            + self._color_list
            + [speed2slowness(self.speed)]
            + [self.mode]
            + [CUSTOM_MODE_TERMINATOR_1, CUSTOM_MODE_TERMINATOR_2]
        )
        return data


_RAINBOW_CROSSFADE = 0x25
_RED_GRADUALLY = 0x26
_GREEN_GRADUALLY = 0x27
_BLUE_GRADUALLY = 0x28
_YELLOW_GRADUALLY = 0x29
_BLUE_GREEN_GRADUALLY = 0x2A
_PURPLE_GRADUALLY = 0x2B
_WHITE_GRADUALLY = 0x2C
_RED_GREEN_CROSSFADE = 0x2D
_RED_BLUE_CROSSFADE = 0x2E
_GREEN_BLUE_CROSSFADE = 0x2F
_RAINBOW_STROBE = 0x30
_RED_STROBE = 0x31
_GREEN_STROBE = 0x32
_BLUE_STROBE = 0x33
_YELLOW_STROBE = 0x34
_BLUE_GREEN_STROBE = 0x35
_PURPLE_STROBE = 0x36
_WHITE_STROBE = 0x37
_RAINBOW_FLASH = 0x38
_NORMAL = 0x61
_CUSTOM = 0x60
_SETUP = 0x63

MODE_GRADUALLY = 0x3A
MODE_JUMP = 0x3B
MODE_STROBE = 0x3C
CUSTOM_MODE_BLANK = (0x1, 0x2, 0x3)

_VALUE_TO_NAME = {
    MODE_GRADUALLY: "GRADUALLY",
    MODE_JUMP: "JUMP",
    MODE_STROBE: "STROBE",
}


RAINBOW_CROSSFADE = Mode(_RAINBOW_CROSSFADE, 1, "RAINBOW_CROSSFADE")
RED_GRADUALLY = Mode(_RED_GRADUALLY, 1, "RED_GRADUALLY")
GREEN_GRADUALLY = Mode(_GREEN_GRADUALLY, 1, "GREEN_GRADUALLY")
BLUE_GRADUALLY = Mode(_BLUE_GRADUALLY, 1, "BLUE_GRADUALLY")
YELLOW_GRADUALLY = Mode(_YELLOW_GRADUALLY, 1, "YELLOW_GRADUALLY")
BLUE_GREEN_GRADUALLY = Mode(_BLUE_GREEN_GRADUALLY, 1, "BLUE_GREEN_GRADUALLY")
PURPLE_GRADUALLY = Mode(_PURPLE_GRADUALLY, 1, "PURPLE_GRADUALLY")
WHITE_GRADUALLY = Mode(_WHITE_GRADUALLY, 1, "WHITE_GRADUALLY")
RED_GREEN_CROSSFADE = Mode(_RED_GREEN_CROSSFADE, 1, "_RED_GREEN_CROSSFADE")
RED_BLUE_CROSSFADE = Mode(_RED_BLUE_CROSSFADE, 1, "RED_BLUE_CROSSFADE")
GREEN_BLUE_CROSSFADE = Mode(_GREEN_BLUE_CROSSFADE, 1, "GREEN_BLUE_CROSSFADE")
RAINBOW_STROBE = Mode(_RAINBOW_STROBE, 1, "RAINBOW_STROBE")
RED_STROBE = Mode(_RED_STROBE, 1, "RED_STROBE")
GREEN_STROBE = Mode(_GREEN_STROBE, 1, "GREEN_STROBE")
BLUE_STROBE = Mode(_BLUE_STROBE, 1, "BLUE_STROBE")
YELLOW_STROBE = Mode(_YELLOW_STROBE, 1, "YELLOW_STROBE")
BLUE_GREEN_STROBE = Mode(_BLUE_GREEN_STROBE, 1, "BLUE_GREEN_STROBE")
PURPLE_STROBE = Mode(_PURPLE_STROBE, 1, "PURPLE_STROBE")
WHITE_STROBE = Mode(_WHITE_STROBE, 1, "WHITE_STROBE")
RAINBOW_FLASH = Mode(_RAINBOW_FLASH, 1, "RAINBOW_FLASH")
NORMAL = Mode(_NORMAL, 1, "NORMAL")
CUSTOM = Mode(_CUSTOM, 1, "CUSTOM")
SETUP_MODE = Mode(_SETUP, 1, "SETUP")

_VALUE_TO_MODE = {
    _RAINBOW_CROSSFADE: RAINBOW_CROSSFADE,
    _RED_GRADUALLY: RED_GRADUALLY,
    _GREEN_GRADUALLY: GREEN_GRADUALLY,
    _BLUE_GRADUALLY: BLUE_GRADUALLY,
    _YELLOW_GRADUALLY: YELLOW_GRADUALLY,
    _BLUE_GREEN_GRADUALLY: BLUE_GREEN_GRADUALLY,
    _PURPLE_GRADUALLY: PURPLE_GRADUALLY,
    _WHITE_GRADUALLY: WHITE_GRADUALLY,
    _RED_GREEN_CROSSFADE: RED_GREEN_CROSSFADE,
    _RED_BLUE_CROSSFADE: RED_BLUE_CROSSFADE,
    _GREEN_BLUE_CROSSFADE: GREEN_BLUE_CROSSFADE,
    _RAINBOW_STROBE: RAINBOW_STROBE,
    _GREEN_STROBE: GREEN_STROBE,
    _BLUE_STROBE: BLUE_STROBE,
    _YELLOW_STROBE: YELLOW_STROBE,
    _BLUE_GREEN_STROBE: BLUE_GREEN_STROBE,
    _PURPLE_STROBE: PURPLE_STROBE,
    _WHITE_STROBE: WHITE_STROBE,
    _RAINBOW_FLASH: RAINBOW_FLASH,
    _NORMAL: NORMAL,
    _CUSTOM: CUSTOM,
    _SETUP: SETUP_MODE,
}
