"""
Package: src.tests
Filename: test_opportunity_registry.py
Author(s): Grant W

Description: Tests for the opportunity registry
"""
# Python Imports
from unittest.mock import patch
import json

# Third Party Imports
import requests
import pytest

# Dynata Imports
import dynata_rex

# Local Imports
from .shared import (ACCESS_KEY,
                     SECRET_KEY,
                     BASE_URL,
                     ResponseMock,
                     TEST_DATA)

REGISTRY = dynata_rex.OpportunityRegistry(ACCESS_KEY, SECRET_KEY, BASE_URL)


def test_format_base_url_adds_https_scheme():
    fake_url = 'missing_fake_base_url.com'
    url = REGISTRY._format_base_url(fake_url)
    assert url == f'https://{fake_url}'


def test_invalid_shard_current_greater_than_total():
    with pytest.raises(dynata_rex.exceptions.InvalidShardException):
        _ = dynata_rex.OpportunityRegistry(
            ACCESS_KEY,
            SECRET_KEY,
            shard_count=1,
            current_shard=2
        )


@patch.object(requests.Session, "post")
def test__get_opportunity(session_post):
    """_get_opportunity should return the json data from response as a dict"""
    data = TEST_DATA['test_get_opportunity']
    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )

    r = REGISTRY._get_opportunity('1234567')

    assert isinstance(r, dict)


@patch.object(requests.Session, "post")
def test_get_opportunity(session_post):
    """get_opportunity should return the json data from response loaded
    into an Opportunity object"""
    data = TEST_DATA['test_get_opportunity']
    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )

    r = REGISTRY.get_opportunity('1234567')

    assert isinstance(r, dynata_rex.models.Opportunity)


@patch.object(requests.Session, "post")
def test__receive_notifications(session_post):
    """_receive_notifications should return the json data from response as a
    list of dicts"""
    data = TEST_DATA['test_receive_notifications']
    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )

    r = REGISTRY._receive_notifications()

    assert isinstance(r, list)

    for opportunity in r:
        assert isinstance(opportunity, dict)


@patch.object(requests.Session, "post")
def test_receive_notifications(session_post):
    """_receive_notifications should return the json data from response as a
    list of Opportunity objects"""
    data = TEST_DATA['test_receive_notifications']
    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )
    r = REGISTRY.receive_notifications()

    assert isinstance(r, list)

    for opportunity in r:
        assert isinstance(opportunity, dynata_rex.models.Opportunity)


@patch.object(dynata_rex.OpportunityRegistry, "ack_notification")
@patch.object(requests.Session, "post")
def test_receive_notifications_assert_ack_for_invalid_opportunity(session_post,
                                                               ack_method):
    """receive notifications should 'ack' a notification returned
    that it cannot convert into an Opportunity object"""
    data = TEST_DATA['test_receive_notifications']

    # Append an invalid Opportunity
    data.append(
        {
            "id": 999999,
            "status": "CLOSED",
            "client_id": None,
            "length_of_interview": 10,
            "invalid_field": "invalid_value"
        }
    )
    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )
    REGISTRY.receive_notifications()

    # Make sure the ack method was called for the invalid opportunity
    assert ack_method.call_count == 1


@patch.object(dynata_rex.OpportunityRegistry, "ack_notifications")
@patch.object(requests.Session, "post")
def test_ack_notification(session_post, ack_method):
    data = TEST_DATA['test_receive_notifications'][0]

    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )
    REGISTRY.ack_notification(data['id'])

    assert ack_method.call_count == 1

    # Make sure we called parent `ack_notifications` method with
    # [ data['id'] ]
    assert ack_method.call_args == (([data['id']],),)


@patch.object(requests.Session, "post")
def test_ack_notifications(session_post):
    """receive notifications should 'ack' an opportunity returned
       that it cannot convert into an Opportunity object"""

    data = [x['id'] for x in TEST_DATA['test_receive_notifications']]

    session_post.return_value = ResponseMock._response_mock(
        204, content_type="application/json"
    )

    REGISTRY.ack_notifications(data)

    assert session_post.call_count == 1
    assert session_post.call_args[1]['data'] == json.dumps(data)


@patch.object(requests.Session, "post")
def test_list_project_opportunities(session_post):
    data = [17039, 17344, 17038, 17040, 17041, 17042]

    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )
    res = REGISTRY.list_project_opportunities(99999)

    assert session_post.call_args[1]['data'] == json.dumps({
        'project_id': 99999,
    })
    assert res == data


@patch.object(requests.Session, "post")
def test_download_collection(session_post):
    """list opportunities should 'ack' an opportunity returned
       that it cannot convert into an Opportunity object"""

    data = TEST_DATA['test_download_collection']

    session_post.return_value = ResponseMock._response_mock(
        200, content=data, content_type="text/csv"
    )

    r = REGISTRY.download_collection('1234567')

    assert isinstance(r, list)
