"""
Package: src.tests
Filename: test_helpers.py
Author(s): Grant W

Description: Test our helpers
"""
# Python Imports
from unittest.mock import patch
import random
import time

# Third Party Imports
import requests
import pytest

# Dynata Imports
import dynata_rex

# Local Imports


def test_make_session():
    """Test the make_session helper"""

    session = dynata_rex.helpers.make_session()

    assert isinstance(session, requests.Session)

    assert session.headers["User-Agent"] == 'rex-sdk-python/0.0.1'

    assert isinstance(session.adapters['https://'],
                      dynata_rex.helpers.TimeoutHTTPAdapter)
    assert isinstance(session.adapters['http://'],
                      dynata_rex.helpers.TimeoutHTTPAdapter)


@patch.object(requests.adapters.HTTPAdapter, 'send')
def test_timeout_adapter_raises_timeout_exception(adapter_send):
    session = dynata_rex.helpers.make_session()
    with pytest.raises(dynata_rex.exceptions.HttpTimeoutException):
        adapter_send.side_effect = requests.exceptions.ReadTimeout()
        session.get('http://example.com')
        session.get('https://example.com')


@patch.object(dynata_rex.helpers.TimeoutHTTPAdapter, '_wait')
@patch.object(requests.adapters.HTTPAdapter, 'send')
def test_timeout_adapter_raises_rex_exception(adapter_send, wait_method):
    session = dynata_rex.helpers.make_session()
    adapter_send.side_effect = requests.exceptions.ConnectionError()
    with pytest.raises(dynata_rex.exceptions.RexServiceException):
        session.get('https://example.com')
        assert wait_method.call_count == dynata_rex.helpers.DEFAULT_RETRIES


@patch.object(time, 'sleep')
@patch.object(random, 'randint')
def test_wait_method(randint_func, sleep_func):
    randint_func.return_value = 1000
    sleep_func.return_value = None

    adapter = dynata_rex.helpers.TimeoutHTTPAdapter(request_timeout=1)

    adapter._wait(1)
    assert sleep_func.call_count == 1

    # should sleep 3 seconds for 1st try, where randint returns 1000
    assert sleep_func.call_args[0][0] == 3


@patch.object(requests.adapters.HTTPAdapter, 'send')
def test_request_timeout_in_kwargs(parent_send_adapter):
    """Test that the request_timeout is passed to the adapter"""
    default_timeout = 10
    desired_timeout_for_request = 20

    adapter = dynata_rex.helpers.TimeoutHTTPAdapter(
        request_timeout=default_timeout)

    adapter.send(requests.Request('GET',
                 'http://example.com'),
                 request_timeout=desired_timeout_for_request)

    assert parent_send_adapter.call_args[1]['timeout'] == \
        desired_timeout_for_request
