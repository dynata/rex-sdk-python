"""
Package: src.tests
Filename: test_requester.py
Author(s): Grant W

Description: Test our requester

NOTE: Requester mainly uses a TTL (seconds from current time), so we have to
mock the expiration date generated quite a bit in here
"""
# Python Imports
from unittest.mock import patch
import pytest
import json

# Third Party Imports
import requests

# Dynata Imports
import dynata_rex
from dynata_rex.signer import RexRequest, Signer

# Local Imports
from .shared import (ACCESS_KEY,
                     SECRET_KEY,
                     DEFAULT_PARAMETERS,
                     TEST_DATE_STR,
                     ResponseMock)

REQUESTER = RexRequest(ACCESS_KEY, SECRET_KEY)


@patch.object(Signer, "create_expiration_date")
def test_create_auth_headers(fun):
    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR
    signature = \
        '6aa2d187875966c2c75fd2cd4db5bbb2de4bafab2494ced8154e3c3b0a906006'
    signing_string = \
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    expect = {
        'dynata-expiration': TEST_DATE_STR,
        'dynata-access-key': ACCESS_KEY,
        'dynata-signature': signature,
        'dynata-signing-string': signing_string
    }
    headers = REQUESTER._create_auth_headers()

    for key, val in headers.items():
        assert key in expect.keys()
        assert expect[key] == val


@patch.object(Signer, "create_expiration_date")
def test_create_auth_headers_additional_params(fun):
    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR
    signature = \
        '6aa2d187875966c2c75fd2cd4db5bbb2de4bafab2494ced8154e3c3b0a906006'
    signing_string = \
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    base = {
        'dynata-expiration': TEST_DATE_STR,
        'dynata-access-key': ACCESS_KEY,
        'dynata-signature': signature,
        'dynata-signing-string': signing_string
    }
    expect = dict(base, **DEFAULT_PARAMETERS)
    headers = REQUESTER._create_auth_headers(
        additional_headers=DEFAULT_PARAMETERS)

    for key, val in headers.items():
        assert key in expect.keys()
        assert expect[key] == val


@patch.object(requests.Session, "get")
def test_get_504_raises_timeout_exception(fun):

    fun.return_value = ResponseMock._504()

    with pytest.raises(dynata_rex.exceptions.HttpTimeoutException):
        REQUESTER.get('https://not-a-real-url-abcdefg.com')


@patch.object(requests.Session, "post")
def test_post_504_raises_timeout_exception(fun):

    fun.return_value = ResponseMock._504()

    with pytest.raises(dynata_rex.exceptions.HttpTimeoutException):
        REQUESTER.post('https://not-a-real-url-abcdefg.com', data='{}')


@patch.object(requests.Session, "get")
def test_get_5XX_raises_service_exception(fun):

    status_codes = list(range(400, 600))
    status_codes.remove(504)  # 504 is handled differently

    for status_code in status_codes:
        fun.return_value = ResponseMock._response_mock(status_code)
        with pytest.raises(dynata_rex.exceptions.RexServiceException):
            REQUESTER.get('https://not-a-real-url-abcdefg.com')


@patch.object(requests.Session, "post")
def test_post_5XX_raises_service_exception(fun):

    status_codes = list(range(400, 600))
    status_codes.remove(504)  # 504 is handled differently

    for status_code in status_codes:
        fun.return_value = ResponseMock._response_mock(status_code)
        with pytest.raises(dynata_rex.exceptions.RexServiceException):
            REQUESTER.post('https://not-a-real-url-abcdefg.com', data='{}')


@patch.object(requests.Session, "get")
def test_get_returns_dict_from_json(fun):

    fun.return_value = ResponseMock._response_mock(
        200,
        content=json.dumps({"whoo": "hoo"}),
        content_type="application/json"
    )

    r = REQUESTER.get('https://not-a-real-url-abcdefg.com')
    assert isinstance(r, dict)


@patch.object(requests.Session, "post")
def test_post_returns_dict_from_json(fun):

    fun.return_value = ResponseMock._response_mock(
        200,
        content=json.dumps({"whoo": "hoo"}),
        content_type="application/json"
    )

    r = REQUESTER.post('https://not-a-real-url-abcdefg.com', data='{}')
    assert isinstance(r, dict)


@patch.object(requests.Session, "get")
def test_get_returns_content_from_non_json(fun):

    fun.return_value = ResponseMock._response_mock(
        200,
        content="hello",
        content_type="text/plain"
    )

    r = REQUESTER.get('https://not-a-real-url-abcdefg.com')
    assert isinstance(r, str)


@patch.object(requests.Session, "post")
def test_post_returns_content_from_non_json(fun):

    fun.return_value = ResponseMock._response_mock(
        200,
        content="hello",
        content_type="text/plain"
    )

    r = REQUESTER.post('https://not-a-real-url-abcdefg.com', data='{}')
    assert isinstance(r, str)
