# file: src/click/src/click/core.py:1788-1791
# asked: {"lines": [1788, 1789, 1790, 1791], "branches": []}
# gained: {"lines": [1788, 1789, 1790, 1791], "branches": []}

import pytest
import click
from click.core import Context, Group

def test_group_collect_usage_pieces():
    """Test that Group.collect_usage_pieces includes subcommand_metavar."""
    # Create a group with a custom subcommand_metavar
    group = Group(name='test_group', subcommand_metavar='SUBCOMMAND [OPTIONS]')
    
    # Create a mock context
    ctx = Context(group)
    
    # Call the method under test
    result = group.collect_usage_pieces(ctx)
    
    # Verify that the result includes the subcommand_metavar
    assert 'SUBCOMMAND [OPTIONS]' in result
    
    # Verify that the result is a list
    assert isinstance(result, list)
    
    # Verify that the subcommand_metavar is appended to the result
    # from the parent class's collect_usage_pieces
    assert result[-1] == 'SUBCOMMAND [OPTIONS]'

def test_group_collect_usage_pieces_default_metavar():
    """Test that Group.collect_usage_pieces uses default subcommand_metavar."""
    # Create a group without specifying subcommand_metavar (should use default)
    group = Group(name='test_group')
    
    # Create a mock context
    ctx = Context(group)
    
    # Call the method under test
    result = group.collect_usage_pieces(ctx)
    
    # Verify that the result includes the default subcommand_metavar
    assert 'COMMAND [ARGS]...' in result
    
    # Verify that the result is a list
    assert isinstance(result, list)
    
    # Verify that the subcommand_metavar is appended to the result
    assert result[-1] == 'COMMAND [ARGS]...'

def test_group_collect_usage_pieces_chain_mode():
    """Test that Group.collect_usage_pieces uses chain mode subcommand_metavar."""
    # Create a group in chain mode
    group = Group(name='test_group', chain=True)
    
    # Create a mock context
    ctx = Context(group)
    
    # Call the method under test
    result = group.collect_usage_pieces(ctx)
    
    # Verify that the result includes the chain mode subcommand_metavar
    assert 'COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...' in result
    
    # Verify that the result is a list
    assert isinstance(result, list)
    
    # Verify that the subcommand_metavar is appended to the result
    assert result[-1] == 'COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...'
