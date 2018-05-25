# python-magichue
Control Magic Hue in Python.


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

Another features are in development.
