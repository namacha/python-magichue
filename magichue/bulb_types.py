BULB_NORMAL = 0x44
BULB_TAPE = 0x33


def str_bulb_type(bulb_type):
    if bulb_type == BULB_NORMAL:
        return 'NORMAL'
    if bulb_type == BULB_TAPE:
        return 'TAPE'
    else:
        return 'UNKNOWN'
