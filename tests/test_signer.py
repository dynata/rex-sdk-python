"""
Package: src.tests
Filename: test_signer.py
Author(s): Grant W

Description: Tests for signature
"""
# Python Imports
from unittest.mock import patch

# Third Party Imports

# Dynata Imports
from dynata_rex.signer import Signer

# Local Imports
from .shared import (ACCESS_KEY,
                     SECRET_KEY,
                     SIGNING_STRING,
                     TEST_DATE_STR,
                     DEFAULT_PARAMETERS)

SIGNER = Signer(ACCESS_KEY, SECRET_KEY)


def test_is_expired_static_date():
    date_str = "1970-01-01T00:00:00.000Z"
    assert SIGNER.is_expired(date_str)


def test_is_expired_generated_date():
    date_str = SIGNER.create_expiration_date(ttl=0)
    assert SIGNER.is_expired(date_str)


def test_is_expired_false_static_date():
    # TODO: If you are reading this in 2099 you should change the date
    date_str = "2099-01-01T00:00:00.000Z"
    assert not SIGNER.is_expired(date_str)


def test_is_expired_false_generated_date():
    date_str = SIGNER.create_expiration_date(ttl=1000)
    assert not SIGNER.is_expired(date_str)


@patch.object(Signer, "create_expiration_date")
def test_generate_signature_from_ttl(fun):
    expect = "f42747bca8a7d0f5ad6adb6eca7c1dd87f7af0b8f9612fba80950fea6e4eff35"

    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    sig, exp = SIGNER.sign_from_ttl(ACCESS_KEY, SECRET_KEY, ttl=0)

    assert sig == expect
    assert exp == TEST_DATE_STR


def test_generate_signature_from_date_str():
    expect = "f42747bca8a7d0f5ad6adb6eca7c1dd87f7af0b8f9612fba80950fea6e4eff35"
    sig, exp = SIGNER.sign_from_expiration_date(ACCESS_KEY,
                                                SECRET_KEY,
                                                TEST_DATE_STR)

    assert sig == expect
    assert exp == TEST_DATE_STR


@patch.object(Signer, "create_expiration_date")
def test_generate_signature_from_ttl_with_signing_string(fun):
    expect = "69e7fcb4a34d5141a368f938f44227a4f264032549ccdc62bd3e652c23e4a8c4"

    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    sig, exp = SIGNER.sign_from_ttl(ACCESS_KEY,
                                    SECRET_KEY,
                                    ttl=0,
                                    signing_string=SIGNING_STRING)

    assert sig == expect
    assert exp == TEST_DATE_STR


def test_generate_signature_from_date_str_with_signing_string():
    expect = "69e7fcb4a34d5141a368f938f44227a4f264032549ccdc62bd3e652c23e4a8c4"
    sig, exp = SIGNER.sign_from_expiration_date(ACCESS_KEY,
                                                SECRET_KEY,
                                                TEST_DATE_STR,
                                                signing_string=SIGNING_STRING)

    assert sig == expect
    assert exp == TEST_DATE_STR


def test_create_query_params_signing_string():
    expect = "13198b48d1ed3ae8d8e2d066fc76cd8b731cea99e3d6f30d9c05ef2e107b4a66"
    sha = SIGNER._create_query_params_signing_string(DEFAULT_PARAMETERS)
    assert sha == expect


def test_sign_query_params_from_expiration_date():
    sig = "035c7ea7c2a7660df6bd8b18a8c6a2b83d869b44c0509e0cb425b460cebbaea4"
    expect = (
        "param_1=value_1"
        "&param_2=value_2"
        "&access_key=access_key"
        "&expiration=1970-01-01T00%3A00%3A00.000Z"
        f"&signature={sig}"
    )
    signed = SIGNER.sign_query_params_from_expiration_date(DEFAULT_PARAMETERS,
                                                           TEST_DATE_STR)
    assert signed == expect


def test_sign_query_params_from_expiration_date_as_dict():
    sig = "035c7ea7c2a7660df6bd8b18a8c6a2b83d869b44c0509e0cb425b460cebbaea4"
    expect = {
        "param_1": "value_1",
        "param_2": "value_2",
        "access_key": ACCESS_KEY,
        "expiration": TEST_DATE_STR,
        "signature": sig
    }
    signed = SIGNER.sign_query_params_from_expiration_date(DEFAULT_PARAMETERS,
                                                           TEST_DATE_STR,
                                                           as_dict=True)
    assert isinstance(signed, dict)
    assert signed == expect


@patch.object(Signer, "create_expiration_date")
def test_sign_query_params_from_ttl(fun):
    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    sig = "035c7ea7c2a7660df6bd8b18a8c6a2b83d869b44c0509e0cb425b460cebbaea4"
    expect = (
        "param_1=value_1"
        "&param_2=value_2"
        "&access_key=access_key"
        "&expiration=1970-01-01T00%3A00%3A00.000Z"
        f"&signature={sig}"
    )
    signed = SIGNER.sign_query_params_from_ttl(DEFAULT_PARAMETERS,
                                               TEST_DATE_STR)
    assert signed == expect


@patch.object(Signer, "create_expiration_date")
def test_sign_query_params_from_ttl_as_dict(fun):
    # Mock return from create_expiration_date()
    fun.return_value = TEST_DATE_STR

    sig = "035c7ea7c2a7660df6bd8b18a8c6a2b83d869b44c0509e0cb425b460cebbaea4"
    expect = {
        "param_1": "value_1",
        "param_2": "value_2",
        "access_key": ACCESS_KEY,
        "expiration": TEST_DATE_STR,
        "signature": sig
    }
    signed = SIGNER.sign_query_parameters_from_ttl(DEFAULT_PARAMETERS,
                                                   TEST_DATE_STR,
                                                   as_dict=True)
    assert isinstance(signed, dict)
    assert signed == expect
