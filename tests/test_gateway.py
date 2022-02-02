"""
Package: src.tests
Filename: test_gateway.py
Author(s): Gino T

Description: Test our requester

NOTE: Requester mainly uses a TTL (seconds from current time), so we have to
mock the expiration date generated quite a bit in here
"""
# Python Imports
from unittest.mock import patch
from urllib.parse import urlparse, parse_qsl
from pytest import raises
import json

# Third Party Imports
import requests

# Dynata Imports
from dynata_rex.respondent_gateway import RespondentGateway
from dynata_rex.signer import Signer, RexRequest
from dynata_rex.models import GatewayDispositionsEnum, GatewayStatusEnum
from dynata_rex.exceptions import SignatureExpiredException, SignatureInvalidException
# Local Imports
from .shared import ACCESS_KEY, SECRET_KEY, TEST_DATE_STR, ResponseMock

GATEWAY = RespondentGateway(ACCESS_KEY, SECRET_KEY, "https://respondent.rex.dynata.com", )
REQUESTER = RexRequest(ACCESS_KEY, SECRET_KEY)


@patch.object(Signer, "create_expiration_date")
def test_create_respondent_url(fun):
    expected = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
               "&language=es" \
               "&birth_date=1989-09-16" \
               "&gender=male&postal_code=00000" \
               "&respondent_id=12345" \
               "&access_key=access_key" \
               "&expiration=1970-01-01T00:00:00.000Z" \
               "&signature=3d063d93efde81823ca0e224c2458cc6053da0f0ce2ff5833644c8e5eddbc594"

    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    signed_url = GATEWAY.create_respondent_url(
                                  'https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58'
                                  '-43db-4370-977d-d14fa4356930&language=es',
                                  '1989-09-16',
                                  'male',
                                  '00000',
                                  '12345')
    assert expected == signed_url


@patch.object(Signer, "create_expiration_date")
def test_create_respondent_url_additional_params(fun):
    expected = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
               "&language=es" \
               "&param1=popcorn" \
               "&birth_date=1989-09-16" \
               "&gender=male" \
               "&postal_code=00000" \
               "&respondent_id=12345" \
               "&access_key=access_key" \
               "&expiration=1970-01-01T00:00:00.000Z" \
               "&signature=5c4c8748a1d91a1407f7da76f4a5a24a3116b0bd94d9326722a5913ac99cb2a3"


    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    signed_url = GATEWAY.create_respondent_url(
        'https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58'
        '-43db-4370-977d-d14fa4356930&language=es',
        '1989-09-16',
        'male',
        '00000',
        '12345',
        {'param1': 'popcorn'})

    assert expected == signed_url


@patch.object(Signer, "create_expiration_date")
def test_create_respondent_url_url_quoting(fun):
    expected = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
               "&language=es" \
               "&birth_date=1989-09-16" \
               "&gender=male&postal_code=00000" \
               "&respondent_id=12345" \
               "&access_key=access_key" \
               "&expiration=1970-01-01T00%3A00%3A00.000Z" \
               "&signature=3d063d93efde81823ca0e224c2458cc6053da0f0ce2ff5833644c8e5eddbc594"

    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    signed_url = GATEWAY.create_respondent_url(
        'https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58'
        '-43db-4370-977d-d14fa4356930&language=es',
        '1989-09-16',
        'male',
        '00000',
        '12345',
        {},
        None, True)

    assert expected == signed_url


@patch.object(Signer, "create_expiration_date")
def test_sign_url_url_quota(fun):
    expected = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
               "&language=es" \
               "&access_key=access_key" \
               "&expiration=1970-01-01T00%3A00%3A00.000Z" \
               "&signature=69f06a6d0f4efba81a62c1eca08decfb64acc0461ea994ce7ae24fb99f7f9e11"

    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    signed_url = GATEWAY.sign_url(
        'https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58'
        '-43db-4370-977d-d14fa4356930&language=es',
        None,
        True
    )
    assert expected == signed_url


@patch.object(Signer, "create_expiration_date")
def test_sign_url(fun):
    expected = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
               "&language=es" \
               "&access_key=access_key" \
               "&expiration=1970-01-01T00:00:00.000Z" \
               "&signature=69f06a6d0f4efba81a62c1eca08decfb64acc0461ea994ce7ae24fb99f7f9e11"

    # Mock return from create_expiration_date()
    fun.return_value = "1970-01-01T00:00:00.000Z"

    signed_url = GATEWAY.sign_url(
        'https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58'
        '-43db-4370-977d-d14fa4356930&language=es',
        None,
        False
    )
    assert expected == signed_url

@patch.object(Signer, "create_expiration_date")
def test_verify_query_params(fun):
    url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
          "&language=es" \
          "&access_key=access_key" \
          "&expiration=2099-01-01T00:00:00.000Z" \
          "&signature=e3bc08b50ac9aa261255828f741467a956c40c4ce1f0e29bb1bcd23b81f31959"

    # Mock return from create_expiration_date()
    fun.return_value = "2099-01-01T00:00:00.000Z"
    parsed = urlparse(url)
    query_parameters = dict(parse_qsl(parsed.query))

    assert GATEWAY.verify_query_parameters(query_parameters, 'access_key')

@patch.object(Signer, "create_expiration_date")
def test_verify_query_params_signature_expired(fun):
    with raises(SignatureExpiredException) as excinfo:
        url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
              "&language=es" \
              "&access_key=access_key" \
              "&expiration=2002-01-01T00:00:00.000Z" \
              "&signature=e3bc08b50ac9aa261255828f741467a956c40c4ce1f0e29bb1bcd23b81f31959"

        # Mock return from create_expiration_date()
        fun.return_value = "2002-01-01T00:00:00.000Z"
        parsed = urlparse(url)
        query_parameters = dict(parse_qsl(parsed.query))
        GATEWAY.verify_query_parameters(query_parameters, 'access_key')
    assert excinfo.type == SignatureExpiredException


@patch.object(Signer, "create_expiration_date")
def test_verify_query_params_signature_invalid(fun):
    with raises(SignatureInvalidException) as excinfo:
        url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
              "&language=es" \
              "&access_key=access_key" \
              "&expiration=2099-01-01T00:00:00.000Z" \
              "&signature=weewerwerer23r2"

        # Mock return from create_expiration_date()
        fun.return_value = "2099-01-01T00:00:00.000Z"
        parsed = urlparse(url)
        query_parameters = dict(parse_qsl(parsed.query))
        GATEWAY.verify_query_parameters(query_parameters, 'access_key')
    assert excinfo.type == SignatureInvalidException

@patch.object(Signer, "create_expiration_date")
def test_verify_query_params_no_access_no_secret(fun):
    url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
          "&language=es" \
          "&expiration=2099-01-01T00:00:00.000Z" \
          "&signature=e3bc08b50ac9aa261255828f741467a956c40c4ce1f0e29bb1bcd23b81f31959"

    # Mock return from create_expiration_date()
    fun.return_value = "2099-01-01T00:00:00.000Z"
    parsed = urlparse(url)
    query_parameters = dict(parse_qsl(parsed.query))

    assert GATEWAY.verify_query_parameters(query_parameters)

@patch.object(Signer, "create_expiration_date")
def test_verify_query_params_secret_and_access_keys(fun):
    url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
          "&language=es" \
          "&access_key=access_key" \
          "&secret_key=secret_key" \
          "&expiration=2099-01-01T00:00:00.000Z" \
          "&signature=386b8ad95a284f9e944dd012dfc92c1872790a9bad2e00e19b57c346fb725629"

    # Mock return from create_expiration_date()
    fun.return_value = "2099-01-01T00:00:00.000Z"
    parsed = urlparse(url)
    query_parameters = dict(parse_qsl(parsed.query))

    assert GATEWAY.verify_query_parameters(query_parameters, 'access_key', 'secret_key')


def test_get_respondent_disposition_complete():
    url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
          "&language=es" \
          "&access_key=access_key" \
          "&secret_key=secret_key" \
          "&disposition=1" \
          "&expiration=2099-01-01T00:00:00.000Z" \
          "&signature=386b8ad95a284f9e944dd012dfc92c1872790a9bad2e00e19b57c346fb725629"

    assert GATEWAY.get_respondent_disposition(url) == GatewayDispositionsEnum['COMPLETE']


def test_get_respondent_disposition_does_not_exist():
    with raises(ValueError) as excinfo:
        url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
              "&language=es" \
              "&access_key=access_key" \
              "&secret_key=secret_key" \
              "&disposition=15" \
              "&expiration=2099-01-01T00:00:00.000Z" \
              "&signature=386b8ad95a284f9e944dd012dfc92c1872790a9bad2e00e19b57c346fb725629"
        GATEWAY.get_respondent_disposition(url)
    assert "15 is not a valid GatewayDispositionsEnum" in str(excinfo.value)


def test_get_respondent_status():
    url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
          "&language=es" \
          "&access_key=access_key" \
          "&secret_key=secret_key" \
          "&disposition=1" \
          "&status=0" \
          "&expiration=2099-01-01T00:00:00.000Z" \
          "&signature=386b8ad95a284f9e944dd012dfc92c1872790a9bad2e00e19b57c346fb725629"
    assert GATEWAY.get_respondent_status(url) == GatewayStatusEnum.COMPLETE_DEFAULT


def test_get_respondent_status_does_not_exist():
    with raises(ValueError) as excinfo:
        url = "https://respondent.qa-rex.dynata.com/start?ctx=7c26bf58-43db-4370-977d-d14fa4356930" \
              "&language=es" \
              "&access_key=access_key" \
              "&secret_key=secret_key" \
              "&disposition=1" \
              "&status=15" \
              "&expiration=2099-01-01T00:00:00.000Z" \
              "&signature=386b8ad95a284f9e944dd012dfc92c1872790a9bad2e00e19b57c346fb725629"
        print(GATEWAY.get_respondent_status(url))
    assert "is not a valid GatewayStatusEnum" in str(excinfo.value)


@patch.object(RexRequest, "post")
def test_create_context(fun):
    expected = 12345

    # Mock return from create_expiration_date()
    fun.return_value = {'id': 12345}

    context = GATEWAY.create_context(
        "12345",
        {
                "ctx": "a987dsglh34t435jkhsdg98u",
                "gender": "male",
                "postal_code": "60081",
                "birth_date": "1959-10-05",
                "country": "US"
        }
    )
    assert expected == context


@patch.object(requests.Session, "post")
def test_expire_context(fun):
    fun.return_value = ResponseMock._response_mock(
        200,
        content_type="text/plain"
    )

    context = GATEWAY.expire_context("12345")
    assert context is None

@patch.object(requests.Session, "post")
def test_expire_context(fun):
    expected = {
        "id": "string",
        "expiration": "2019-08-24T14:15:22Z",
        "items": {
            "property1": "string",
            "property2": "string"
        }
    }
    fun.return_value = ResponseMock._response_mock(
        200,
        content=json.dumps({
            "id": "string",
            "expiration": "2019-08-24T14:15:22Z",
            "items": {
                "property1": "string",
                "property2": "string"
            }
        }),
        content_type="text/plain"
    )

    context = GATEWAY.get_context(12345)
    assert context == expected

