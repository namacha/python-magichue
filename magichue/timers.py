

class Timer:

    FALSE = 0x0f
    TRUE = 0xf0
    Mon = 0x02
    Tue = 0x04
    Wed = 0x08
    Thu = 0x10
    Fri = 0x20
    Sat = 0x40
    Sun = 0x80

    def __init__(self, data=None):
        self.empty = False
        self.enabled = None
        self.year = None
        self.month = None
        self.date = None
        self.hour = None
        self.minute = None
        self.week = None
        self.mode = None
        self.r = None
        self.g = None
        self.b = None
        self.ww = None
        self.on = None
        if data:
            print(data)
            self._parse(data)
            return

    def __repr__(self):
        if self.empty:
            return '<Timer: EMPTY>'
        else:
            return '<Timer: {year}/{month}/{date} {hour}:{minute} {enabled}/{on}>'.format(
                year=self.year,
                month=self.month,
                date=self.date,
                hour=self.hour,
                minute=self.minute,
                enabled= 'ACTIVE' if self.enabled else 'INACTIVE',
                on='ON' if self.on else 'OFF',
            )

    def _parse(self, data):
        if data[13] == 0:
            self.empty = True
            return
        self.enabled = True if data[0] == self.TRUE else False
        self.year = 2000 + data[1]
        self.month, self.date = data[2:4]
        self.hour = data[4]
        self.minute = data[5]
        self.week = data[7]
        self.mode = data[8]
        self.r, self.g, self.b, self.ww = data[9:13]
        self.on = True if data[13] == self.TRUE else False
