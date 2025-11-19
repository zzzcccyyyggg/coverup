# file: src/click/src/click/core.py:3394-3415
# asked: {"lines": [3394, 3395, 3397, 3398, 3399, 3401, 3402, 3404, 3406, 3407, 3408, 3410, 3411, 3413, 3415], "branches": [[3397, 3398], [3397, 3406], [3406, 3407], [3406, 3415]]}
# gained: {"lines": [3394, 3395, 3397, 3398, 3399, 3401, 3402, 3404, 3406, 3407, 3408, 3410, 3411, 3413, 3415], "branches": [[3397, 3398], [3397, 3406], [3406, 3407], [3406, 3415]]}

import pytest
import warnings
import click.core


def test_getattr_basecommand_deprecation():
    """Test that accessing BaseCommand triggers deprecation warning and returns _BaseCommand."""
    with pytest.warns(DeprecationWarning, match="'BaseCommand' is deprecated and will be removed in Click 9.0. Use 'Command' instead.") as record:
        result = getattr(click.core, "BaseCommand")
    
    assert len(record) == 1
    assert record[0].filename == __file__
    assert result is click.core._BaseCommand


def test_getattr_multicommand_deprecation():
    """Test that accessing MultiCommand triggers deprecation warning and returns _MultiCommand."""
    with pytest.warns(DeprecationWarning, match="'MultiCommand' is deprecated and will be removed in Click 9.0. Use 'Group' instead.") as record:
        result = getattr(click.core, "MultiCommand")
    
    assert len(record) == 1
    assert record[0].filename == __file__
    assert result is click.core._MultiCommand


def test_getattr_unknown_attribute():
    """Test that accessing unknown attribute raises AttributeError."""
    with pytest.raises(AttributeError, match="unknown_attr"):
        getattr(click.core, "unknown_attr")
