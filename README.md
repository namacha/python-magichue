# python-magichue
Magichue(as known as Magichome) is a cheap smart led bulb that you can controll hue/saturation/brightnes and power over WiFi. They are available at Amazon or other online web shop.

I tested this library with [this bulb](http://www.amazon.co.jp/exec/obidos/ASIN/B0777LXQ4R/).


# Example
Turn Magichue On/Off.
```python
import magichue


light = magichue.Light('192.168.0.20')  # change address

# Show power status
print(light.on)

# Turn On
light.on = True

# Turn Off
light.on = False

# Show current color 
print(light.rgb)  # => (95, 25, 128)
print(light.r)  # => 95
print(light.g)  # => 25
print(light.b)  # => 128

print(light.is_white)  # => whether warm white LED is using or not.
print(light.w)  # => brightness of warm white LED.

print(light.hue)  # => 0.7799352750809061
print(light.saturation)  # => 0.8046875
print(light.brightness)  # => 128


# Changing Color
# By rgb
light.rgb = (128, 64, 32)

# By individual rgb value
light.r = 255
light.g = 128
light.b = 32

# By hue/saturation/brightness
# Hue and Saturation should be 0 to 255
light.hue = 0.3
light.saturation = 0.6
# Brightness should be 0 to 255
light.brightness = 255

# Use Warm White bulb
light.is_white = True
light.brightness = 255

```

Other features are in development.
