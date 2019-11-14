# python-magichue

![demo](https://github.com/namacha/python-magichue/raw/image/hue.gif)

Magichue(as known as Magichome) is a cheap smart led bulb that you can controll hue/saturation/brightnes and power over WiFi. They are available at Amazon or other online web shop.

I tested this library with [this bulb](http://www.amazon.co.jp/exec/obidos/ASIN/B0777LXQ4R/).

# Example
Rainbow cross-fade.
```python
import time
import magichue


light = magichue.Light('192.168.0.20')  # change address
if not light.on:
    light.on = True

if light.is_white:
  light.is_white = False

light.rgb = (255, 255, 255)

for hue in range(1000):
    light.hue = hue / 1000
    time.sleep(0.05)

```


# Installation
```
$ pip install python-magichue
```

# Usage
import magichue.
```python
import magichue
light = magichue.Light('192.168.0.20')
```

## Power State

### Getting power status.
```python
print(light.on)  # => True if light is on else False
```

### Setting light on/off.
```python
light.on = True
light.on = False
```

## Getting color
This shows a tuple of current RGB.
```python
print(light.rgb)
```
or access individually.
```python
print(light.r)
print(light.g)
print(light.b)
```

## Warm White bulb
Magichue has a two types of leds. One is rgb led and the other is warm white led.
To use warm white led, do as following.
```python
light.is_white = True
# light.is_white = False  # This disables warm white led.
```

**If warm white is enabled, you can't change color of bulb!**
So, you need to execute ``` light.is_white = False ``` before changing color.


## Setting color
### By rgb
```python
light.rgb = (128, 0, 32)
```
or
```python
light.r = 200
light.g = 0
light.b = 32
```

### By hsb
```python
light.hue = 0.3
light.saturation = 0.6
light.brightness = 255
```
hue, saturation are float value from 0 to 1. brightness is a integer value from 0 to 255.
These variables are also readable.

### Note about stripe bulb
Stripe bulb doesn't seem to allow jump to another color when you change color.
To disable fading effect,
```python
light.rgb = (128, 0, 20)  # It fades
light.allow_fading = False  # True by default
light.rgb = (20, 0, 128)  # Jumps
```


## Changing mode
Magichue blub has a built-in flash patterns.

To check current mode, just
```python
print(light.mode_str)  # string name of mode
print(light.mode)  # integer value
```

and changing modes,
```python
light.mode = magichue.RAINBOW_CROSSFADE
```


These are built-in modes.
```
RAINBOW_CROSSFADE
RED_GRADUALLY
GREEN_GRADUALLY
BLUE_GRADUALLY
YELLOW_GRADUALLY
BLUE_GREEN_GRADUALLY
PURPLE_GRADUALLY
WHITE_GRADUALLY
RED_GREEN_CROSSFADE
RED_BLUE_CROSSFADE
GREEN_BLUE_CROSSFADE
RAINBOW_STROBE
GREEN_STROBE
BLUE_STROBE
YELLOW_STROBE
BLUE_GREEN_STROBE
PURPLE_STROBE
WHITE_STROBE
RAINBOW_FLASH
NORMAL
```


### Changing the speed of mode

speed is a float value from 0 to 1.

```python
print(light.speed)

light.speed = 0.5  # set speed to 50%
```




### Custom Modes
You can create custom light flash patterns.

**mode**
- MODE_JUMP
- MODE_GRADUALLY
- MODE_STROBE

**speed**
A float value 0 to 1

**colors**
A list of rgb(tuple or list) which has less than 17 length.

```python
from magichue import (
    CustomMode,
    MODE_JUMP,
)


# Creating Mode
mypattern1 = CustomMode(
    mode=MODE_JUMP,
    speed=0.5,
    colors=[
        (128, 0, 32),
        (100, 20, 0),
        (30, 30, 100),
        (0, 0, 50)
    ]
)

# Apply Mode
light.mode = mypattern1
```





Other features are in development.
