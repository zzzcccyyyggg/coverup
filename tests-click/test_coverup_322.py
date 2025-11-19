# file: src/click/src/click/core.py:1684-1687
# asked: {"lines": [1684, 1685, 1687], "branches": []}
# gained: {"lines": [1684, 1685], "branches": []}

import pytest
import click
from click.testing import CliRunner
import typing as t

def test_group_decorator_overload():
    """Test that the group decorator overload signature is properly defined."""
    # This test verifies that the @t.overload decorator for the group method
    # is properly defined and accessible. We're testing the type annotation
    # signature specifically.
    
    # Create a group instance
    group = click.Group('test_group')
    
    # The overload decorator doesn't leave a trace on the runtime method
    # We can verify the method exists and is callable
    assert hasattr(group, 'group')
    assert callable(group.group)
    
    # Test that we can use the overloaded signature pattern
    # by calling group with *args and **kwargs and getting a callable back
    decorator_factory = group.group('subgroup', help='test subgroup')
    assert callable(decorator_factory)

def test_group_decorator_with_args_kwargs():
    """Test the group decorator with arguments and keyword arguments."""
    # This test exercises the overload signature that takes *args and **kwargs
    # and returns a callable that takes a function and returns a Group
    
    runner = CliRunner()
    
    # Create a parent group
    @click.group()
    def parent():
        pass
    
    # Use the group decorator with arguments to create a subcommand
    @parent.group('subgroup', help='A subgroup')
    def subgroup():
        pass
    
    # Add a command to the subgroup to verify it works
    @subgroup.command()
    def subcommand():
        click.echo('subcommand executed')
    
    # Test that the hierarchy works correctly
    result = runner.invoke(parent, ['subgroup', 'subcommand'])
    assert result.exit_code == 0
    assert 'subcommand executed' in result.output

def test_group_decorator_as_decorator_factory():
    """Test that group can be used as a decorator factory."""
    runner = CliRunner()
    
    # Create a parent group
    @click.group()
    def parent():
        pass
    
    # Use group as a decorator factory (without immediate function)
    subgroup_decorator = parent.group('subgroup')
    
    # Then apply it to a function
    @subgroup_decorator
    def subgroup():
        pass
    
    # Add a command to verify it works
    @subgroup.command()
    def subcommand():
        click.echo('subcommand from factory')
    
    # Test execution
    result = runner.invoke(parent, ['subgroup', 'subcommand'])
    assert result.exit_code == 0
    assert 'subcommand from factory' in result.output

def test_group_decorator_type_annotations():
    """Test that the group decorator properly handles type annotations."""
    # This test specifically targets the overload signature that returns
    # t.Callable[[t.Callable[..., t.Any]], Group]
    
    @click.group()
    def cli():
        pass
    
    # Test that the decorator returns the expected type when used with arguments
    decorator = cli.group('test')
    
    # The decorator should be callable and accept a function
    @decorator
    def test_group():
        pass
    
    # Verify the result is a Group instance
    assert isinstance(test_group, click.Group)
    assert test_group.name == 'test'
