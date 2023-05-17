"""
Package: dynata-rex.models
Filename: respondent_gateway.py
Author(s): Grant W

Description: Implementation of dataclasses for Respondent Gateway
"""
# Python Imports
from enum import Enum
from typing import Optional


class GatewayGenderEnum(Enum):
    MALE = 1
    FEMALE = 2


class GatewayDispositionsEnum(Enum):
    UNKNOWN = 0
    COMPLETE = 1
    TERMINATION = 2
    OVERQUOTA = 3
    DUPLICATE = 4
    QUALITY = 5


class GatewayStatusEnum(Enum):
    """
    Composite status code from Disposition + non-unique status code
    Must call as tuple of Gateway Disposition + Status code
    ie
    >>> disp_code, status_code = 1, 0
    >>> disp = GatewayDispositionsEnum(disp_code)
    >>> status = RespondentGatewayStatusEnum((disp, status_code))
    >>> status.name
    'COMPLETE_DEFAULT`
    >>> status.value
    (<GatewayDispositionsEnum.COMPLETE: 1>, 0)
    """
    UNKNOWN_DEFAULT = GatewayDispositionsEnum.UNKNOWN, 0
    COMPLETE_DEFAULT = GatewayDispositionsEnum.COMPLETE, 0
    COMPLETE_PARTIAL = GatewayDispositionsEnum.COMPLETE, 1
    TERMINATION_DYNATA = GatewayDispositionsEnum.TERMINATION, 1
    TERMINATION_CLIENT = GatewayDispositionsEnum.TERMINATION, 2
    OVERQUOTA_DYNATA = GatewayDispositionsEnum.OVERQUOTA, 1
    OVERQUOTA_CLIENT = GatewayDispositionsEnum.OVERQUOTA, 2
    DUPLICATE_DEFAULT = GatewayDispositionsEnum.DUPLICATE, 0
    QUALITY_ANSWER = GatewayDispositionsEnum.QUALITY, 1
    QUALITY_SPEEDING = GatewayDispositionsEnum.QUALITY, 2
    QUALITY_SUSPENDED = GatewayDispositionsEnum.QUALITY, 3


class Attribute:

    def __init__(self, attribute_id: int, answers: list[int]):
        self.id = attribute_id
        self.answers = answers

    def __iter__(self):
        yield from {
            "id": self.id,
            "answers": self.answers
        }.items()

    def __str__(self):
        return str(dict(self))

    def to_json(self):
        return dict(self)


class PutRespondentRequest:
    def __init__(self, respondent_id: str,
                 language: str,
                 country: str,
                 gender: Optional[str],
                 birth_date: Optional[str],
                 postal_code: Optional[str],
                 attributes: Optional[list[Attribute]]):
        self.respondent_id = respondent_id
        self.language = language
        self.country = country
        self.gender = gender
        self.birth_date = birth_date
        self.postal_code = postal_code
        self.attributes = attributes

    def __iter__(self):
        yield from {
            "respondent_id": self.respondent_id,
            "language": self.language,
            "country": self.country,
            "gender": self.gender,
            "birth_date": self.birth_date,
            "postal_code": self.postal_code,
            "attributes": [
                attribute.to_json() for attribute in self.attributes
            ],
        }.items()

    def __str__(self):
        return str(dict(self))

    def to_json(self):
        return dict(self)


class PutRespondentAnswersRequest:
    def __init__(self,
                 respondent_id: str,
                 attributes: list[Attribute]):
        self.respondent_id = respondent_id
        self.attributes = attributes

    def __iter__(self):
        yield from {
            "respondent_id": self.respondent_id,
            "attributes": [
                attribute.to_json() for attribute in self.attributes
            ]
        }.items()

    def __str__(self):
        return str(dict(self))

    def to_json(self):
        return dict(self)
