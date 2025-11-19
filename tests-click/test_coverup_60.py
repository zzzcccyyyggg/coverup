# file: src/click/src/click/core.py:3164-3190
# asked: {"lines": [3164, 3174, 3176, 3177, 3179, 3180, 3181, 3182, 3184, 3185, 3187, 3188, 3190], "branches": [[3176, 3177], [3176, 3179], [3179, 3184], [3179, 3190], [3187, 3188], [3187, 3190]]}
# gained: {"lines": [3164, 3174, 3176, 3177, 3179, 3180, 3181, 3182, 3184, 3185, 3187, 3188, 3190], "branches": [[3176, 3177], [3176, 3179], [3179, 3184], [3179, 3190], [3187, 3188], [3187, 3190]]}

import os
import pytest
from click.core import Context, Option, Command

class TestOptionResolveEnvvarValue:
    """Test cases for Option.resolve_envvar_value method to achieve full coverage."""
    
    def test_resolve_envvar_value_with_existing_envvar(self, monkeypatch):
        """Test when environment variable from envvar property exists."""
        # Setup
        ctx = Context(Command('test'))
        option = Option(['--test'], envvar='CUSTOM_ENVVAR')
        monkeypatch.setenv('CUSTOM_ENVVAR', 'custom_value')
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result == 'custom_value'
    
    def test_resolve_envvar_value_with_auto_envvar_prefix_all_conditions_met(self, monkeypatch):
        """Test when auto_envvar_prefix is set and all conditions are met."""
        # Setup
        ctx = Context(Command('test'), auto_envvar_prefix='MYAPP')
        option = Option(['--test-option'], allow_from_autoenv=True)
        envvar_name = 'MYAPP_TEST_OPTION'
        monkeypatch.setenv(envvar_name, 'auto_env_value')
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result == 'auto_env_value'
    
    def test_resolve_envvar_value_with_auto_envvar_prefix_but_no_envvar(self, monkeypatch):
        """Test when auto_envvar_prefix is set but environment variable doesn't exist."""
        # Setup
        ctx = Context(Command('test'), auto_envvar_prefix='MYAPP')
        option = Option(['--test-option'], allow_from_autoenv=True)
        # Don't set the environment variable
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result is None
    
    def test_resolve_envvar_value_with_auto_envvar_prefix_but_allow_from_autoenv_false(self):
        """Test when auto_envvar_prefix is set but allow_from_autoenv is False."""
        # Setup
        ctx = Context(Command('test'), auto_envvar_prefix='MYAPP')
        option = Option(['--test-option'], allow_from_autoenv=False)
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result is None
    
    def test_resolve_envvar_value_with_auto_envvar_prefix_but_no_ctx_auto_envvar_prefix(self):
        """Test when allow_from_autoenv is True but ctx.auto_envvar_prefix is None."""
        # Setup
        ctx = Context(Command('test'), auto_envvar_prefix=None)
        option = Option(['--test-option'], allow_from_autoenv=True)
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result is None
    
    def test_resolve_envvar_value_with_auto_envvar_prefix_but_no_option_name(self):
        """Test when allow_from_autoenv is True but option has no name."""
        # Setup
        ctx = Context(Command('test'), auto_envvar_prefix='MYAPP')
        option = Option(['--test-option'], allow_from_autoenv=True)
        option.name = None  # Simulate option without name
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result is None
    
    def test_resolve_envvar_value_with_empty_envvar_value(self, monkeypatch):
        """Test when auto_envvar_prefix environment variable exists but has empty value."""
        # Setup
        ctx = Context(Command('test'), auto_envvar_prefix='MYAPP')
        option = Option(['--test-option'], allow_from_autoenv=True)
        envvar_name = 'MYAPP_TEST_OPTION'
        monkeypatch.setenv(envvar_name, '')  # Empty string
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result is None
    
    def test_resolve_envvar_value_inheritance_from_parent(self, monkeypatch):
        """Test that parent context's auto_envvar_prefix is inherited."""
        # Setup
        parent_ctx = Context(Command('parent'), auto_envvar_prefix='PARENT')
        ctx = Context(Command('child'), parent=parent_ctx, info_name='child')
        option = Option(['--test'], allow_from_autoenv=True)
        envvar_name = 'PARENT_CHILD_TEST'
        monkeypatch.setenv(envvar_name, 'inherited_value')
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result == 'inherited_value'
    
    def test_resolve_envvar_value_with_super_returning_value(self, monkeypatch):
        """Test when super().resolve_envvar_value returns a value."""
        # Setup
        ctx = Context(Command('test'))
        option = Option(['--test'], envvar='EXISTING_ENVVAR')
        monkeypatch.setenv('EXISTING_ENVVAR', 'super_value')
        
        # Execute
        result = option.resolve_envvar_value(ctx)
        
        # Assert
        assert result == 'super_value'
        # Verify that auto_envvar_prefix logic was not executed due to early return
