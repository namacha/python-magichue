BULB_RGBWW = 0x44
BULB_TAPE = 0x33
BULB_RGBWWCW = 0x35


def str_bulb_type(bulb_type):
    if bulb_type == BULB_RGBWW:
        return "rgbww"
    if bulb_type == BULB_TAPE:
        return "tape"
    if bulb_type == BULB_RGBWWCW:
        return "rgbwwcw"
    else:
        return "UNKNOWN"
