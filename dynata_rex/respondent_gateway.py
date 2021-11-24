"""
Package: src.dynata_rex
Filename: respondent_gateway.py
Author(s): Grant W

Description: Respondent Gateway interactions
"""
# Python Import
from urllib.parse import urlparse, parse_qsl, unquote
from typing import Union
from copy import copy

# Third Party Imports

# Local Imports
from dynata_rex.models import GatewayDispositionsEnum, GatewayStatusEnum
from .signer import Signer
from .exceptions import SignatureExpiredException, SignatureInvalidException


class RespondentGateway:
    """
    Respondent Gateway interactions
    """

    def __init__(self,
                 access_key: str,
                 secret_key: str,
                 default_ttl: int = 10):
        """
        @access_key: liam access key for REX
        @secret_key: liam secret key for REX

        # Optional
        @ttl: time to live for signature in seconds
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.default_ttl = default_ttl
        self.signer = Signer(access_key, secret_key, default_ttl=default_ttl)

    def sign_url(self,
                 url,
                 ttl: Union[int, None] = None,
                 url_quoting: bool = False) -> str:
        """
        Sign a URL with the given access and secret keys

        @url: URL to sign
        @ttl: time to live for signature in seconds
        @url_quoting: whether to URL quote the returned URL
        """
        if not ttl:
            ttl = self.default_ttl
        parsed = urlparse(url)
        query_parameters = dict(parse_qsl(parsed.query))
        signed_params = self.signer.sign_query_parameters_from_ttl(
            query_parameters, ttl=ttl)
        updated = parsed._replace(query=signed_params).geturl()
        if url_quoting:
            return updated
        return unquote(updated)

    def verify_query_parameters(self,
                                query_parameters: dict,
                                access_key: str = None,
                                secret_key: str = None) -> bool:
        """
        Verify a signature on query parameters match the expected output
        from a pair of access and secret keys. Returns True if the signature
        matches, False otherwise.

        @query_parameters: dictionary of query parameters

        Optional
        @access_key: liam access key for signing
        @secret_key: liam secret key for signing
        """
        parameters = copy(query_parameters)
        if access_key is None:
            access_key = self.access_key
        if secret_key is None:
            secret_key = self.secret_key
        expiration_date_str = parameters.pop('expiration')
        if self.signer.is_expired(expiration_date_str):
            raise SignatureExpiredException
        original_signature = parameters.pop('signature')
        signed = self.signer.sign_query_params_from_expiration_date(
            parameters, expiration_date_str, access_key, secret_key,
            as_dict=True
        )
        if original_signature != signed['signature']:
            raise SignatureInvalidException
        return True

    def verify_url(self,
                   url,
                   access_key: str = None,
                   secret_key: str = None) -> bool:
        """
        Verify a URL's signature matches for the given access and secret keys
        """
        if access_key is None:
            access_key = self.access_key
        if secret_key is None:
            secret_key = self.secret_key
        parsed = urlparse(url)
        query_parameters = dict(parse_qsl(parsed.query))
        try:
            return self.verify_query_parameters(query_parameters,
                                                access_key=access_key,
                                                secret_key=secret_key)
        except (KeyError,
                SignatureExpiredException,
                SignatureInvalidException):
            return False

    def get_respondent_disposition(
            self, url) -> Union[GatewayDispositionsEnum, None]:
        """
        Get the disposition of a respondent from a URL
        """
        parsed = urlparse(url)
        query_parameters = dict(parse_qsl(parsed.query))
        try:
            disposition = int(query_parameters['disposition'])
            return GatewayDispositionsEnum(disposition)
        except KeyError:
            return None

    def get_respondent_status(
            self, url) -> Union[GatewayStatusEnum, None]:
        """
        Get the status of a respondent from a URL
        """
        parsed = urlparse(url)
        query_parameters = dict(parse_qsl(parsed.query))
        disposition = self.get_respondent_disposition(url)
        if not disposition:
            return None
        try:
            status = int(query_parameters['status'])
            return GatewayStatusEnum((disposition, status))
        except KeyError:
            return None
