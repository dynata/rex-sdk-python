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
def test__list_opportunities(session_post):
    """_list_opportunities should return the json data from response as a
    list of dicts"""
    data = TEST_DATA['test_list_opportunities']
    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )

    r = REGISTRY._list_opportunities()

    assert isinstance(r, list)

    for opportunity in r:
        assert isinstance(opportunity, dict)


@patch.object(requests.Session, "post")
def test_list_opportunities(session_post):
    """_get_opportunity should return the json data from response as a
    list of Opportunity objects"""
    data = TEST_DATA['test_list_opportunities']
    session_post.return_value = ResponseMock._response_mock(
        200, content=json.dumps(data), content_type="application/json"
    )
    r = REGISTRY.list_opportunities()

    assert isinstance(r, list)

    for opportunity in r:
        assert isinstance(opportunity, dynata_rex.models.Opportunity)


@patch.object(dynata_rex.OpportunityRegistry, "ack_opportunity")
@patch.object(requests.Session, "post")
def test_list_opportunities_assert_ack_for_invalid_opportunity(session_post,
                                                               ack_method):
    """list opportunities should 'ack' an opportunity returned
    that it cannot convert into an Opportunity object"""
    data = TEST_DATA['test_list_opportunities']

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
    REGISTRY.list_opportunities()

    # Make sure the ack method was called for the invalid opportunity
    assert ack_method.call_count == 1
