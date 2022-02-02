"""
Package: src.tests
Filename: test_models_base.py
Author(s): Grant W

Description: Test for the base models we implement
"""
# Python Imports
from typing import List

# Third Party Imports
import pytest

# Dynata Imports
import dynata_rex

# Local Imports


def test_base_object():
    """Test the base object"""

    class TestObject(dynata_rex.models.base.BaseObject):
        pass

    test_object = TestObject()

    assert str(test_object) == "<dynata_rex.TestObject>"


def test_hashable_model():

    class TestModel(dynata_rex.models.base.HashableModel):
        attribute_one: str
        attribute_two: str

    test_model_one = TestModel(attribute_one="one", attribute_two="one")
    test_model_two = TestModel(attribute_one="two", attribute_two="two")

    # Set uses __hash__ to compare objects
    models = set([test_model_one, test_model_two])

    assert len(models) == 2


def test_hashable_model_with_submodel():

    class TestSubModel(dynata_rex.models.base.HashableModel):
        attribute_three: str
        attribute_four: str

    class TestModel(dynata_rex.models.base.HashableModel):
        attribute_one: str
        attribute_two: str
        attribute_three: List[TestSubModel]

    sub_model_one = TestSubModel(attribute_three="one", attribute_four="one")
    sub_model_two = TestSubModel(attribute_three="two", attribute_four="two")

    test_model_one = TestModel(attribute_one="one",
                               attribute_two="one",
                               attribute_three=[sub_model_one])

    test_model_two = TestModel(attribute_one="two",
                               attribute_two="two",
                               attribute_three=[sub_model_two])

    # Set uses __hash__ to compare objects
    models = set([test_model_one, test_model_two])

    assert len(models) == 2


def test_fallback_enum():

    class TestEnum(dynata_rex.models.base.FallbackEnum):
        DEFAULT = "default"

    test_enum = TestEnum('missing_value')
    assert test_enum.value == "default"


def test_fallback_enum_raises_value_error_when_undefined():

    class TestEnum(dynata_rex.models.base.FallbackEnum):
        pass

    with pytest.raises(ValueError):
        _ = TestEnum('missing')
