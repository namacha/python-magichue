import random
import logging
import hashlib
from string import (
    ascii_uppercase,
    digits
)
import requests

from .commands import Command


API_BASE = 'https://wifij01us.magichue.net/app'
UA = 'Magic Hue/1.2.2 (IOS,13.400000,ja_JP)'

_LOGGER = logging.getLogger(__name__)


class HTTPError(Exception):
    pass


class MagicHueAPIError(Exception):
    pass


class RemoteAPI:

    def __init__(self, token):
        self.token = token

    @classmethod
    def auth(
        cls,
        user: str,
        password: str,
        client_id : str = ''
    ):
        if not client_id:
            client_id = ''.join(
                [random.choice(ascii_uppercase + digits) for _ in range(32)]
            )
        payload = {
            'userID': user,
            'password': hashlib.md5(password.encode('utf8')).hexdigest(),
            'clientID': client_id,
        }
        _LOGGER.debug(f'Logging in with email {user}')
        res = requests.post(
            API_BASE+'/login/MagicHue',
            json=payload,
            headers={'User-Agent': UA}
        )
        if res.status_code != 200:
            raise HTTPError
        if res.json().get('code') != 0:
            raise MagicHueAPIError(res.json().get('msg'))
        _LOGGER.debug(f'Login successful')
        return res.json().get('token')

    @classmethod
    def login_with_user_password(
        cls,
        user: str,
        password: str,
        client_id : str = ''
    ):
        token = cls.auth(user, password, client_id)
        return RemoteAPI(token=token)

    @classmethod
    def login_with_token(
        cls,
        token: str
    ):
        return RemoteAPI(token)

    def _post_with_token(self, endpoint, payload):
        _LOGGER.debug(f'Sending POST request to {endpoint}, payload={payload}')
        res = requests.post(
            API_BASE + endpoint,
            json=payload,
            headers={'User-Agent': UA, 'token':self.token}
        )
        _LOGGER.debug(f'Got response({res.status_code}): {res.text}')
        if res.status_code != 200:
            raise HTTPError
        if res.json().get('code') != 0:
            raise MagicHueAPIError(res.json().get('msg'))
        return res.json()

    def _get_with_token(self, endpoint):
        _LOGGER.debug(f'Sending GET request to {endpoint}')
        res = requests.get(
            API_BASE + endpoint,
            headers={'User-Agent': UA, 'token':self.token}
        )
        _LOGGER.debug(f'Got response({res.status_code}): {res.text}')
        if res.status_code != 200:
            raise HTTPError
        if res.json().get('code') != 0:
            raise MagicHueAPIError(res.json().get('msg'))
        return res.json()

    def _send_request(self, cmd: Command, macaddr: str):
        payload = {
            "hexData": cmd.hex_string(is_remote=True),
            "macAddress": macaddr,
            "responseCount": cmd.response_len
        }
        result = self._post_with_token('/sendRequestCommand/MagicHue', payload)
        return result

    def _send_command(self, cmd: Command, macaddr: str):
        payload = {
            "dataCommandItems": [{
                "hexData": cmd.hex_string(),
                "macAddress": macaddr
            }]
        }
        result = self._post_with_token('/sendCommandBatch/MagicHue', payload)
        return result

    def get_devices(self):
        result = self._get_with_token('/getMyBindDevicesAndState/MagicHue')
        return result
