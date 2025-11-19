# file: src/click/src/click/core.py:1733-1776
# asked: {"lines": [1733, 1762, 1763, 1765, 1766, 1767, 1769, 1770, 1771, 1773, 1774, 1776], "branches": [[1765, 1766], [1765, 1769]]}
# gained: {"lines": [1733, 1762, 1763, 1765, 1766, 1767, 1769, 1770, 1771, 1773, 1774, 1776], "branches": [[1765, 1766], [1765, 1769]]}

import pytest
import click
from click.testing import CliRunner

def test_group_result_callback_no_existing_callback():
    """Test result_callback when no existing callback is present."""
    group = click.Group('test_group')
    
    @group.result_callback()
    def callback(result, **kwargs):
        return result + 10
    
    assert group._result_callback is callback

def test_group_result_callback_replace_existing():
    """Test result_callback with replace=True to replace existing callback."""
    group = click.Group('test_group')
    
    @group.result_callback()
    def first_callback(result, **kwargs):
        return result + 5
    
    @group.result_callback(replace=True)
    def second_callback(result, **kwargs):
        return result + 10
    
    assert group._result_callback is second_callback

def test_group_result_callback_chain_callbacks():
    """Test result_callback chains multiple callbacks when replace=False."""
    group = click.Group('test_group')
    
    @group.result_callback()
    def first_callback(result, **kwargs):
        return result + 5
    
    @group.result_callback()
    def second_callback(result, **kwargs):
        return result + 10
    
    # The chained function should be a wrapper, not the original second_callback
    assert group._result_callback is not first_callback
    assert callable(group._result_callback)
    
    # Test that the chained callback works correctly
    result = group._result_callback(100, input=20)
    assert result == 115  # 100 + 5 + 10

def test_group_result_callback_with_args_and_kwargs():
    """Test result_callback with both positional and keyword arguments."""
    group = click.Group('test_group')
    
    @group.result_callback()
    def first_callback(result, *args, **kwargs):
        return result + sum(args) + kwargs.get('extra', 0)
    
    @group.result_callback()
    def second_callback(result, *args, **kwargs):
        return result * 2
    
    # Test the chained callback with args and kwargs
    result = group._result_callback(10, 5, 3, extra=2)
    assert result == 40  # (10 + 5 + 3 + 2) * 2 = 20 * 2 = 40

def test_group_result_callback_update_wrapper_preservation():
    """Test that update_wrapper preserves function attributes."""
    group = click.Group('test_group')
    
    @group.result_callback()
    def first_callback(result, **kwargs):
        """First callback docstring."""
        return result + 1
    
    first_callback.custom_attr = "test_value"
    
    @group.result_callback()
    def second_callback(result, **kwargs):
        """Second callback docstring."""
        return result + 2
    
    # Check that the wrapper preserves attributes from the second callback
    assert group._result_callback.__name__ == second_callback.__name__
    assert group._result_callback.__doc__ == second_callback.__doc__
    assert hasattr(group._result_callback, 'custom_attr') is False  # Should have second callback's attributes
