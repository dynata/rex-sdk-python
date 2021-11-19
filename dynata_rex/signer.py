"""
Package: src
Filename: auth.py
Author(s): Grant W
"""
# Python Imports
import hashlib
import hmac
import os
from datetime import datetime, timedelta
import json
from typing import Union

# Third Party Imports

# Local Imports
from .logs import logger
from .helpers import make_session
from .exceptions import HttpTimeoutException, RexServiceException

DEFAULT_TTL_SECONDS = os.environ.get('DEFAULT_TTL_SECONDS', 10)
DEFAULT_SIGNING_STRING = os.environ.get('DEFAULT_SIGNING_STRING', '')


def create_expiration_date(ttl: int) -> str:
    """
    Create a formatted date string from now + ttl in seconds
    - expected format:         "2021-03-30T14:17:29.208Z"
    - python isoformat outputs '2021-03-30T14:17:29.208292', so we have to
      strip the last 3, and append the Z.
    :ttl : int - seconds
    """
    return (datetime.utcnow() + timedelta(seconds=ttl)) \
        .isoformat(timespec="milliseconds") + "Z"


def sign(access_key: str,
         secret_key: str,
         ttl: int,
         signing_string: str = '') -> (str, str):
    """
    Sign 3 times, first with expiration, second with key, final with secret

    :key    : str - liam access key
    :secret : str - liam secret key
    :ttl    : int - ttl in seconds for life of signature
    :signing_string: str - optional string to sign with

    ->tuple (signature: str, expiration_date: str)
    """
    expiration_date_str = create_expiration_date(ttl)
    first = digest(expiration_date_str, signing_string)
    second = digest(access_key, first)
    final = digest(secret_key, second)
    return final, expiration_date_str


def digest(signing_key: str, message: str, encoding='utf-8') -> str:
    """
    Create a digest from signing_key & message
    """
    _hmac = hmac.new(
        key=bytes(signing_key, encoding=encoding),
        msg=bytes(message, encoding=encoding),
        digestmod=hashlib.sha256
    )
    return _hmac.hexdigest()


class Signer:

    def __init__(self,
                 access_key: str,
                 secret_key: str,
                 signing_string: str = DEFAULT_SIGNING_STRING,
                 ttl: int = DEFAULT_TTL_SECONDS):
        self.access_key = access_key
        self.secret_key = secret_key
        self.signing_string = signing_string
        self.ttl = ttl

    def sign(self) -> str:
        return sign(self.access_key,
                    self.secret_key,
                    self.ttl,
                    self.signing_string)


class RexRequest:
    """Wrapper for http calls to include our signature"""

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.signer = Signer(access_key, secret_key)
        self.session = make_session()

    def _signature(self):
        return self.signer.sign()

    def _create_auth_headers(self, additional_headers={}):
        signature, expiration = self._signature()
        base = {
            'dynata-expiration': expiration,
            'dynata-access-key': self.access_key,
            'dynata-signature': signature
        }
        return dict(additional_headers, **base)

    def dispatch(self,
                 url,
                 data=None,
                 method='GET') -> Union[dict, str]:

        additional_headers = {}
        if data:
            additional_headers = {'Content-type': 'application/json'}
            data = json.dumps(data)

        headers = self._create_auth_headers(additional_headers)

        if not hasattr(self.session, method.lower()):
            raise Exception('Invalid http method provided.')

        method = getattr(self.session, method.lower())

        res = method(url, data=data, headers=headers)
        if res.status_code > 299:
            if res.status_code == 504:
                raise HttpTimeoutException(res.content)
            if data:
                logger.warning(data)
            logger.warning(res.__dict__)
            raise RexServiceException(res.content)
        try:
            return res.json()
        except json.decoder.JSONDecodeError as e:
            if res.status_code != 204:
                logger.debug(str(e), res.__dict__, exc_info=1)
        return res.content.decode('utf-8')

    def get(self, url: str):
        return self.dispatch(url)

    def post(self, url, data):
        return self.dispatch(url, data=data, method='POST')
