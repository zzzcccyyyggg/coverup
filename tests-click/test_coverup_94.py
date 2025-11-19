# file: src/click/src/click/core.py:2538-2602
# asked: {"lines": [2538, 2552, 2553, 2555, 2558, 2559, 2560, 2561, 2563, 2564, 2566, 2567, 2569, 2570, 2571, 2572, 2574, 2577, 2578, 2579, 2580, 2581, 2585, 2588, 2589, 2593, 2597, 2598, 2600, 2602], "branches": [[2558, 2563], [2558, 2577], [2580, 2581], [2580, 2585], [2588, 2597], [2588, 2602]]}
# gained: {"lines": [2538, 2552, 2553, 2555, 2558, 2559, 2560, 2561, 2563, 2564, 2566, 2567, 2569, 2570, 2571, 2572, 2574, 2577, 2578, 2579, 2580, 2581, 2585, 2588, 2589, 2593, 2597, 2600, 2602], "branches": [[2558, 2563], [2558, 2577], [2580, 2581], [2580, 2585], [2588, 2597], [2588, 2602]]}

import pytest
from click.core import Option, Context, ParameterSource
from click._utils import UNSET
from click.types import StringParamType
from unittest.mock import Mock, patch
import typing as t

class TestParameterHandleParseResult:
    
    def test_deprecated_parameter_with_explicit_value(self, monkeypatch):
        """Test that deprecated parameter with explicit value shows deprecation warning."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], deprecated=True)
        param.name = 'test'
        param.param_type_name = 'option'
        
        # Mock consume_value to return an explicit value (not from default)
        param.consume_value = Mock(return_value=('test_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value='test_value')
        
        # Mock echo to capture the deprecation message
        echo_calls = []
        monkeypatch.setattr('click.core.echo', lambda msg, err=None: echo_calls.append(msg))
        
        # Mock style to return the message as-is
        monkeypatch.setattr('click.core.style', lambda msg, **kwargs: msg)
        
        opts = {'test': 'test_value'}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value == 'test_value'
        assert result_args == []
        assert len(echo_calls) == 1
        assert 'DeprecationWarning' in echo_calls[0]
        assert 'test' in echo_calls[0]
    
    def test_deprecated_parameter_with_default_value_no_warning(self, monkeypatch):
        """Test that deprecated parameter with default value doesn't show deprecation warning."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], deprecated=True)
        param.name = 'test'
        param.param_type_name = 'option'
        
        # Mock consume_value to return a value from default source
        param.consume_value = Mock(return_value=('default_value', ParameterSource.DEFAULT))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value='default_value')
        
        # Mock echo to capture any calls
        echo_calls = []
        monkeypatch.setattr('click.core.echo', lambda msg, err=None: echo_calls.append(msg))
        
        opts = {}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value == 'default_value'
        assert result_args == []
        assert len(echo_calls) == 0  # No deprecation warning for default values
    
    def test_deprecated_parameter_with_custom_message(self, monkeypatch):
        """Test that deprecated parameter with custom message shows the custom message."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], deprecated="Use --new-test instead")
        param.name = 'test'
        param.param_type_name = 'option'
        
        # Mock consume_value to return an explicit value
        param.consume_value = Mock(return_value=('test_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value='test_value')
        
        # Mock echo to capture the deprecation message
        echo_calls = []
        monkeypatch.setattr('click.core.echo', lambda msg, err=None: echo_calls.append(msg))
        
        # Mock style to return the message as-is
        monkeypatch.setattr('click.core.style', lambda msg, **kwargs: msg)
        
        opts = {'test': 'test_value'}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value == 'test_value'
        assert result_args == []
        assert len(echo_calls) == 1
        assert 'DeprecationWarning' in echo_calls[0]
        assert 'test' in echo_calls[0]
        assert 'Use --new-test instead' in echo_calls[0]
    
    def test_resilient_parsing_with_type_conversion_error(self):
        """Test that resilient parsing handles type conversion errors by setting value to UNSET."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = True
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'])
        param.name = 'test'
        param.expose_value = True
        
        # Mock consume_value to return a value
        param.consume_value = Mock(return_value=('test_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to raise an exception
        param.process_value = Mock(side_effect=ValueError("Invalid value"))
        
        opts = {'test': 'test_value'}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value is UNSET
        assert result_args == []
        assert ctx.params['test'] is UNSET
    
    def test_non_resilient_parsing_with_type_conversion_error(self):
        """Test that non-resilient parsing re-raises type conversion errors."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'])
        param.name = 'test'
        
        # Mock consume_value to return a value
        param.consume_value = Mock(return_value=('test_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to raise an exception
        test_exception = ValueError("Invalid value")
        param.process_value = Mock(side_effect=test_exception)
        
        opts = {'test': 'test_value'}
        args = []
        
        with pytest.raises(ValueError, match="Invalid value"):
            param.handle_parse_result(ctx, opts, args)
    
    def test_expose_value_false_does_not_set_context_param(self):
        """Test that when expose_value is False, the parameter is not added to context.params."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], expose_value=False)
        param.name = 'test'
        
        # Mock consume_value to return a value
        param.consume_value = Mock(return_value=('test_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value='test_value')
        
        opts = {'test': 'test_value'}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value == 'test_value'
        assert result_args == []
        assert 'test' not in ctx.params  # Should not be exposed
    
    def test_expose_value_true_sets_context_param(self):
        """Test that when expose_value is True, the parameter is added to context.params."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], expose_value=True)
        param.name = 'test'
        
        # Mock consume_value to return a value
        param.consume_value = Mock(return_value=('test_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value='test_value')
        
        opts = {'test': 'test_value'}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value == 'test_value'
        assert result_args == []
        assert ctx.params['test'] == 'test_value'  # Should be exposed
    
    def test_expose_value_true_but_param_already_set_does_not_override(self):
        """Test that when expose_value is True but param is already set, it doesn't override."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {'test': 'existing_value'}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], expose_value=True)
        param.name = 'test'
        
        # Mock consume_value to return a value
        param.consume_value = Mock(return_value=('new_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value='new_value')
        
        opts = {'test': 'new_value'}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value == 'new_value'
        assert result_args == []
        assert ctx.params['test'] == 'existing_value'  # Should not override existing value
    
    def test_expose_value_true_but_param_set_to_unset_overrides(self):
        """Test that when expose_value is True and param is UNSET, it overrides."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {'test': UNSET}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], expose_value=True)
        param.name = 'test'
        
        # Mock consume_value to return a value
        param.consume_value = Mock(return_value=('new_value', ParameterSource.COMMANDLINE))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value='new_value')
        
        opts = {'test': 'new_value'}
        args = []
        
        result_value, result_args = param.handle_parse_result(ctx, opts, args)
        
        assert result_value == 'new_value'
        assert result_args == []
        assert ctx.params['test'] == 'new_value'  # Should override UNSET value
    
    def test_deprecated_parameter_with_unset_value_no_warning(self):
        """Test that deprecated parameter with UNSET value doesn't show deprecation warning."""
        ctx = Mock(spec=Context)
        ctx.resilient_parsing = False
        ctx.params = {}
        ctx.set_parameter_source = Mock()
        
        param = Option(['--test'], deprecated=True)
        param.name = 'test'
        param.param_type_name = 'option'
        
        # Mock consume_value to return UNSET value
        param.consume_value = Mock(return_value=(UNSET, ParameterSource.COMMANDLINE))
        
        # Mock process_value to return the same value
        param.process_value = Mock(return_value=UNSET)
        
        # Mock echo - no calls expected
        with patch('click.core.echo') as mock_echo:
            opts = {}
            args = []
            
            result_value, result_args = param.handle_parse_result(ctx, opts, args)
            
            assert result_value is UNSET
            assert result_args == []
            mock_echo.assert_not_called()
