# python-magichue
Magichue is a cheap smart led bulb that you can controll hue/saturate/brightnes and power over WiFi. Thet are available at Amazon or other online web shop.

I tested this library with [this bulb](http://www.amazon.co.jp/exec/obidos/ASIN/B0777LXQ4R/hatena-blog-22/).


# Example
Turn Magichue On/Off.
```python
import magichue


light = magichue.Light('192.168.0.20')  # change address

# Turn On
light.on = True

# Turn Off
light.on = False
```

Other features are in development.
