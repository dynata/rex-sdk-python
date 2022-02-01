"""
Package: src.tests
Filename: shared.py
Author(s): Grant W

Description: Common values and functions for tests
"""
# Python Imports

# Third Party Imports
from requests.models import Response

# Dynata Imports

# Local Imports

ACCESS_KEY = 'access_key'
SECRET_KEY = 'secret_key'

SIGNING_STRING = 'signing_string'
TEST_DATE_STR = "1970-01-01T00:00:00.000Z"
DEFAULT_PARAMETERS = {
    "param_1": "value_1",
    "param_2": "value_2"
}


class ResponseMock:

    @staticmethod
    def _response_mock(status_code,
                       content='',
                       content_type='text/plain'):
        response = Response()
        response.status_code = status_code
        # if content:
        response._content = str.encode(content)
        response.headers['content-type'] = content_type
        return response

    @classmethod
    def _204(cls, *args, **kwargs):
        return cls._response_mock(204)

    @classmethod
    def _504(cls, *args, **kwargs):
        return cls._response_mock(504)
