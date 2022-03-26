__all__ = [
    "speed2slowness",
    "slowness2speed",
]


def speed2slowness(value):
    """speed: float value 0 to 1.0
    slowness: integer value 1 to 31"""
    slowness = int(-30 * value + 31)
    return slowness


def slowness2speed(value):
    """invert function of speed2slowness"""
    speed = (31 - value) / 30
    return speed


def round_value(value, _min, _max):
    if not isinstance(value, (int, float)):
        raise ValueError("Invalid value: value must be a int or float.")
    if value < _min:
        return _min
    if value > _max:
        return _max
    return value
