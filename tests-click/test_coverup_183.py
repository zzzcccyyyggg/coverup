# file: src/click/src/click/core.py:660-665
# asked: {"lines": [660, 662, 663, 664, 665], "branches": [[663, 664], [663, 665]]}
# gained: {"lines": [660, 662, 663, 664, 665], "branches": [[663, 664], [663, 665]]}

import pytest
import click
from click.core import Context

class MockCommand:
    def __init__(self):
        self.allow_extra_args = False
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False

def test_find_root_with_parent():
    """Test find_root when context has a parent."""
    root_command = MockCommand()
    root_ctx = Context(command=root_command, info_name="root")
    
    child_command = MockCommand()
    child_ctx = Context(command=child_command, parent=root_ctx, info_name="child")
    
    grandchild_command = MockCommand()
    grandchild_ctx = Context(command=grandchild_command, parent=child_ctx, info_name="grandchild")
    
    # Test that grandchild finds root
    result = grandchild_ctx.find_root()
    assert result is root_ctx
    assert result.info_name == "root"

def test_find_root_without_parent():
    """Test find_root when context has no parent (is already root)."""
    command = MockCommand()
    ctx = Context(command=command, info_name="root")
    
    # Test that root finds itself
    result = ctx.find_root()
    assert result is ctx
    assert result.info_name == "root"
