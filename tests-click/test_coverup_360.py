# file: src/click/src/click/core.py:854-870
# asked: {"lines": [854, 870], "branches": []}
# gained: {"lines": [854, 870], "branches": []}

import pytest
import click
from click.core import Context, ParameterSource

class TestContextGetParameterSource:
    """Test cases for Context.get_parameter_source method."""
    
    def test_get_parameter_source_existing(self):
        """Test get_parameter_source returns correct source for existing parameter."""
        # Create a mock command
        mock_command = click.Command('test')
        
        # Create context with parameter source data
        ctx = Context(mock_command)
        ctx._parameter_source = {'test_param': ParameterSource.COMMANDLINE}
        
        # Test that existing parameter returns correct source
        result = ctx.get_parameter_source('test_param')
        assert result == ParameterSource.COMMANDLINE
    
    def test_get_parameter_source_nonexistent(self):
        """Test get_parameter_source returns None for non-existent parameter."""
        # Create a mock command
        mock_command = click.Command('test')
        
        # Create context with empty parameter source
        ctx = Context(mock_command)
        ctx._parameter_source = {}
        
        # Test that non-existent parameter returns None
        result = ctx.get_parameter_source('nonexistent_param')
        assert result is None
    
    def test_get_parameter_source_with_different_sources(self):
        """Test get_parameter_source with various parameter sources."""
        # Create a mock command
        mock_command = click.Command('test')
        
        # Create context with multiple parameter sources
        ctx = Context(mock_command)
        ctx._parameter_source = {
            'env_param': ParameterSource.ENVIRONMENT,
            'default_param': ParameterSource.DEFAULT,
            'default_map_param': ParameterSource.DEFAULT_MAP,
            'prompt_param': ParameterSource.PROMPT
        }
        
        # Test each parameter source type
        assert ctx.get_parameter_source('env_param') == ParameterSource.ENVIRONMENT
        assert ctx.get_parameter_source('default_param') == ParameterSource.DEFAULT
        assert ctx.get_parameter_source('default_map_param') == ParameterSource.DEFAULT_MAP
        assert ctx.get_parameter_source('prompt_param') == ParameterSource.PROMPT
    
    def test_get_parameter_source_empty_dict(self):
        """Test get_parameter_source with empty _parameter_source dict."""
        # Create a mock command
        mock_command = click.Command('test')
        
        # Create context with empty parameter source dict
        ctx = Context(mock_command)
        ctx._parameter_source = {}
        
        # Test that any parameter returns None
        result = ctx.get_parameter_source('any_param')
        assert result is None
    
    def test_get_parameter_source_fresh_context(self):
        """Test get_parameter_source on a fresh context (default initialization)."""
        # Create a mock command
        mock_command = click.Command('test')
        
        # Create context without modifying _parameter_source
        # This tests the default initialization from Context.__init__
        ctx = Context(mock_command)
        
        # The _parameter_source should be an empty dict by default
        # Test that any parameter returns None
        result = ctx.get_parameter_source('test_param')
        assert result is None
        # Also verify the _parameter_source is indeed an empty dict
        assert ctx._parameter_source == {}
