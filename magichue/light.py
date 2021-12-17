from abc import ABCMeta, abstractmethod

from .commands import (
    Command,
    TurnON,
    TurnOFF,
)

from .magichue import Status



class AbstractLight(metaclass=ABCMeta):

    on: bool = False
    status: Status = Status()
    allow_fading: bool = False

    @abstractmethod
    def _send_command(self, cmd: Command):
        pass

    @abstractmethod
    def _get_status_data(self):
        pass

    def turn_on(self):
        self._send_command(TurnON)

    def turn_off(self):
        self._send_command(TurnOFF)

    def _update_status(self):
        data = self._get_status_data()
        self.status.parse(data)

    def _apply_status(self):
        data = self.status.make_data()
        cmd = Command.from_array(data)
        self._send_command(cmd)



class RemoteLight(AbstractLight):

    def __init__(self, api, macaddr):
        self.api = api
        self.macaddr = macaddr

    def _send_command(self, cmd):
        self.api._send_command(cmd, self.macaddr)

    @staticmethod
    def str2hexarray(hexstr: str) -> tuple:
        return tuple([int(hexstr[i:i+2], 16) for i in range(0, len(hexstr), 2)])

    def _get_status_data(self):
        data_arr = self.api.get_devices().get('data')
        for dev in data_arr:
            if dev.get('macAddress') == self.macaddr:
                return self.str2hexarray(dev.get('state'))
