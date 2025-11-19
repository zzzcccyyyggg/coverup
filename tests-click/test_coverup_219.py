# file: src/click/src/click/types.py:1205-1209
# asked: {"lines": [1205, 1206, 1207, 1208, 1209], "branches": []}
# gained: {"lines": [1205, 1206, 1207, 1208, 1209], "branches": []}

import pytest
import typing as t
from click.types import OptionHelpExtra


def test_option_help_extra_creation():
    """Test that OptionHelpExtra can be created with all optional fields."""
    # Test creation with envvars
    data1: OptionHelpExtra = {"envvars": ("VAR1", "VAR2")}
    assert data1["envvars"] == ("VAR1", "VAR2")
    
    # Test creation with default
    data2: OptionHelpExtra = {"default": "some_default"}
    assert data2["default"] == "some_default"
    
    # Test creation with range
    data3: OptionHelpExtra = {"range": "0-100"}
    assert data3["range"] == "0-100"
    
    # Test creation with required
    data4: OptionHelpExtra = {"required": "yes"}
    assert data4["required"] == "yes"
    
    # Test creation with multiple fields
    data5: OptionHelpExtra = {
        "envvars": ("VAR1",),
        "default": "default_value",
        "range": "1-10",
        "required": "no"
    }
    assert data5["envvars"] == ("VAR1",)
    assert data5["default"] == "default_value"
    assert data5["range"] == "1-10"
    assert data5["required"] == "no"


def test_option_help_extra_empty():
    """Test that OptionHelpExtra can be created with no fields (all optional)."""
    data: OptionHelpExtra = {}
    assert len(data) == 0
