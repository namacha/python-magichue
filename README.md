# python-magichue

![demo](https://github.com/namacha/python-magichue/raw/image/hue.gif)

Magichue(as known as Magichome, FluxLED, etc.) is a cheap smart led bulb that you can controll hue/saturation/brightnes and power over WiFi. They are available at Amazon or other online web shop.

I tested this library with RGBWWCW(v7), RGB(v8), RGBWW(v8) bulbs.


**Now it is possible to use Remote API !**

# Example
Rainbow cross-fade.
```python
import time
import magichue

user = 'username@example.com'
password = 'password'
api = magichue.RemoteAPI.login_user_password(user=user, password=password)
light = api.get_online_bulbs()[0]

# local_device_ips = magcihue.discover_bulbs()
# light = magichue.LocalLight(local_device_ips[0])


if not light.on:
    light.on = True

if light.is_white:
  light.is_white = False

light.rgb = (0, 0, 0)
light.brightness = 255
light.saturation = 1

for hue in range(1000):
    light.hue = hue / 1000
    time.sleep(0.05)

```


# Installation
```
$ pip install python-magichue
```

# Usage

## Remote API
Now it's available to use MagicHome HTTP API.

You have to login and register your bulb with MagicHome account in advance.
### Login with Username/Password
```python
api = magichue.RemoteAPI.login_with_user_password(user='xxx', password='xxx')
print(api.token)  # you can show TOKEN and save it.
```

### Login with Token
It is recommended to use token string.
```python
TOKEN = 'xxx'
api = magichue.RemoteAPI.login_with_token(TOKEN)
```
### Make bulb instance
```python
TOKEN = 'xxx'
api = magichue.RemoteAPI.login_with_token(TOKEN)
light = RemoteLight(api=api, macaddr='xxx')
```

## Discover bulbs

### Local bulbs
```python
from magichue import discover_bulbs, LocalLight
addrs = discover_bulbs()  # returns list of bulb address
light = magichue.LocalLight(addrs[0])
```

### Remote bulbs
```python
from magichue import RemoteAPI

TOKEN = 'xxx'
api = magichue.RemoteAPI.login_with_token(TOKEN)
online_bulbs = api.get_online_bulbs()
light = online_bulbs[0]

# Getting online device information.
online_devices = api.get_online_devices()
# It is also possible to retrieve all device info binded with your account.
all_devices = api.get_all_devices()
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
# or
light.turn_on()
light.turn_off()
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

## White LEDs
If your bulbs support white leds, you can change brightness(0-255) of white leds.

To use white led,
```python
light.is_white = True
# light.is_white = False  # This disables white led.
```

**If white led is enabled, you can't change color of bulb!**
So, you need to execute ``` light.is_white = False ``` before changing color.

### Warm White(ww)
```python
light.cw = 0
light.w = 255
```

### Cold White (cw)
```python
light.w = 0
light.cw = 255
```
 
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

## Bulb clock
```python
print(light.get_current_time())
```


## Changing mode
Magichue blub has a built-in flash patterns.

To check current mode, just
```python
print(light.mode.name)  # string name of mode
print(light.mode.value)  # integer value
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

---
Other features are in development.

## Debugging
Putting this snippet to begging of your code, this library outputs debug log.
```python
import loggging
logging.basicConfig(level=logging.DEBUG)
```
