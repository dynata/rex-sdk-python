"""
Package: src.tests
Filename: shared.py
Author(s): Grant W

Description: Common values and functions for tests
"""
# Python Imports
import os
import json

# Third Party Imports
from requests.models import Response

# Dynata Imports

# Local Imports

ACCESS_KEY = 'access_key'
SECRET_KEY = 'secret_key'
BASE_URL = 'http://fake-rex-url.dynata.com'

SIGNING_STRING = 'signing_string'
TEST_DATE_STR = "1970-01-01T00:00:00.000Z"
DEFAULT_PARAMETERS = {
    "param_1": "value_1",
    "param_2": "value_2"
}


def load_test_data():
    """Load data out of /data folder so we can use it in our tests"""
    out = {}
    for fn in os.listdir(f"{os.getcwd()}/data"):
        if fn.endswith('.json'):  # ignore non-json
            with open(f'{os.getcwd()}/data/{fn}') as f:
                key = fn.split('.')[0]
                out[key] = json.load(f)
    return out


TEST_DATA = load_test_data()


class ResponseMock:

    @staticmethod
    def _response_mock(status_code,
                       content='',
                       content_type='text/plain'):
        response = Response()
        response.status_code = status_code
        response._content = str.encode(content)
        response.headers['content-type'] = content_type
        return response

    @classmethod
    def _204(cls, *args, **kwargs):
        return cls._response_mock(204)

    @classmethod
    def _504(cls, *args, **kwargs):
        return cls._response_mock(504)
