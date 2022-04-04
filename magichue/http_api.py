import random
import logging
import hashlib
import json
from dataclasses import dataclass
from string import ascii_uppercase, digits
from typing import List

import requests

from .light import RemoteLight
from .commands import Command
from .exceptions import HTTPError, MagicHueAPIError


API_BASE = "https://wifij01us.magichue.net/app"
UA = "Magic Hue/1.2.2 (IOS,13.400000,ja_JP)"

_LOGGER = logging.getLogger(__name__)


@dataclass
class RemoteDevice:

    device_type: int
    version: int
    macaddr: str
    local_ip: str
    state_str: str


class RemoteAPI:
    def __init__(self, token):
        self.token = token

    @staticmethod
    def sanitize_json_text(text: str) -> str:
        """Sometimes MagicHue api returns broken json text which ends with `.`"""
        if text.endswith("."):
            _LOGGER.debug("A junk end of the line. Sanitized")
            return text[:-1]
        return text

    @staticmethod
    def handle_api_response(res: requests.Response):
        clean_text = RemoteAPI.sanitize_json_text(res.text)
        try:
            _decoded = json.loads(clean_text)
        except json.decoder.JSONDecodeError:
            raise MagicHueAPIError("Invalid JSON String: {}".format(clean_text))
        if _decoded.get("code") != 0:
            if _decoded.get("msg"):
                raise MagicHueAPIError(f"{_decoded.get('msg')}")
            raise MagicHueAPIError("Unknown Eror: {}".format(clean_text))
        return _decoded

    @classmethod
    def auth(cls, user: str, password: str, client_id: str = ""):
        if not client_id:
            client_id = "".join(
                [random.choice(ascii_uppercase + digits) for _ in range(32)]
            )
        payload = {
            "userID": user,
            "password": hashlib.md5(password.encode("utf8")).hexdigest(),
            "clientID": client_id,
        }
        _LOGGER.debug("Logging in with email {}".format(user))
        res = requests.post(
            API_BASE + "/login/MagicHue", json=payload, headers={"User-Agent": UA}
        )

        res_dict = cls.handle_api_response(res)
        _LOGGER.debug("Login successful")
        return res_dict.get("token")

    @classmethod
    def login_with_user_password(cls, user: str, password: str, client_id: str = ""):
        token = cls.auth(user, password, client_id)
        return RemoteAPI(token=token)

    @classmethod
    def login_with_token(cls, token: str):
        return RemoteAPI(token)

    def _post_with_token(self, endpoint, payload):
        _LOGGER.debug(
            "Sending POST request to {}, payload={}".format(
                endpoint,
                payload,
            )
        )
        res = requests.post(
            API_BASE + endpoint,
            json=payload,
            headers={"User-Agent": UA, "token": self.token},
        )
        _LOGGER.debug(
            "Got response({}): {}".format(
                res.status_code,
                res.text,
            )
        )
        res_dict = RemoteAPI.handle_api_response(res)
        return res_dict

    def _get_with_token(self, endpoint):
        _LOGGER.debug("Sending GET request to {}".format(endpoint))
        res = requests.get(
            API_BASE + endpoint, headers={"User-Agent": UA, "token": self.token}
        )
        _LOGGER.debug(
            "Got response({}): {}".format(
                res.status_code,
                res.text,
            )
        )
        res_dict = RemoteAPI.handle_api_response(res)
        return res_dict

    def _send_request(self, cmd: Command, macaddr: str):
        payload = {
            "hexData": cmd.hex_string(is_remote=True),
            "macAddress": macaddr,
            "responseCount": cmd.response_len,
        }
        result = self._post_with_token("/sendRequestCommand/MagicHue", payload)
        return result["data"]

    def _send_command(self, cmd: Command, macaddr: str):
        payload = {
            "dataCommandItems": [{"hexData": cmd.hex_string(), "macAddress": macaddr}]
        }
        result = self._post_with_token("/sendCommandBatch/MagicHue", payload)
        return result

    def get_online_bulbs(self, online_only=True) -> List[RemoteLight]:
        devices = self.get_online_devices(online_only=online_only)
        bulbs = [
            RemoteLight(api=self, macaddr=dev.macaddr)
            for dev in devices
        ]
        return bulbs

    def get_online_devices(self, online_only=True) -> List[RemoteDevice]:
        result = self._get_with_token("/getMyBindDevicesAndState/MagicHue")
        arr = result.get("data")
        _LOGGER.debug("Found {} devices".format(len(arr)))
        devices = []
        for dev_dict in arr:
            if online_only and not dev_dict.get("isOnline"):
                continue
            dev = RemoteDevice(
                device_type=dev_dict.get("deviceType"),
                version=dev_dict.get("ledVersionNum"),
                macaddr=dev_dict.get("macAddress"),
                local_ip=dev_dict.get("localIP"),
                state_str=dev_dict.get("state"),
            )
            devices.append(dev)
        return devices

    def get_all_devices(self):
        return self.get_online_devices(online_only=False)
