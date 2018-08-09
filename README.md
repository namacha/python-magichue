# python-magichue
Magichue(as known as Magichome) is a cheap smart led bulb that you can controll hue/saturation/brightnes and power over WiFi. They are available at Amazon or other online web shop.

I tested this library with [this bulb](http://www.amazon.co.jp/exec/obidos/ASIN/B0777LXQ4R/).


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
To use warm white led, do as below.
```python
light.is_white = True
# light.is_white = False  # This disables warm white led.
```
If warm white is enabled, you can't set color to bulb.


## Setting color
### By rgb
```python
light.rgb = (128, 0, 32)
```
or
```python
light.r = 200
```

### By hsb
```python
light.hue = 0.3
light.saturation = 0.6
light.brightness = 255
```
hue, saturation are float value from 0 to 1. brightness is a integer value from 0 to 255.
These variables are also readable.



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

Other features are in development.
