# file: src/click/src/click/core.py:1002-1025
# asked: {"lines": [1002, 1003, 1004, 1006, 1007, 1009, 1010, 1012, 1013, 1014, 1016, 1017, 1019, 1022, 1025], "branches": [[1006, 1007], [1006, 1009], [1009, 1010], [1016, 1017], [1016, 1025]]}
# gained: {"lines": [1002, 1003, 1004, 1006, 1007, 1009, 1010, 1012, 1013, 1014, 1016, 1017, 1019, 1022, 1025], "branches": [[1006, 1007], [1006, 1009], [1009, 1010], [1016, 1017], [1016, 1025]]}

import pytest
import warnings
from click.core import Command, Context, Option, Parameter

class TestCommandGetParams:
    """Test cases for Command.get_params method to achieve full coverage."""
    
    def test_get_params_with_help_option(self):
        """Test get_params when help option is added."""
        ctx = Context(Command('test'))
        cmd = Command('test', add_help_option=True)
        
        params = cmd.get_params(ctx)
        
        # Should have help option added
        assert len(params) > 0
        # The last parameter should be the help option
        assert any('--help' in param.opts for param in params)
    
    def test_get_params_without_help_option(self):
        """Test get_params when help option is not added."""
        ctx = Context(Command('test'))
        cmd = Command('test', add_help_option=False)
        
        params = cmd.get_params(ctx)
        
        # Should not have help option
        assert len(params) == 0
    
    def test_get_params_with_duplicate_opts_debug_mode(self):
        """Test get_params with duplicate options when __debug__ is True."""
        # This test assumes __debug__ is True (default in development)
        # We'll test the duplicate detection logic directly
        
        ctx = Context(Command('test'))
        
        # Create command with duplicate options
        opt1 = Option(['--test', '-t'])
        opt2 = Option(['--test', '-t'])  # Duplicate option
        
        cmd = Command('test', params=[opt1, opt2], add_help_option=False)
        
        # Capture warnings - they should be raised when __debug__ is True
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            params = cmd.get_params(ctx)
            
            # Check if warnings were raised (depends on __debug__)
            if __debug__:
                # Should have warning about duplicate option
                assert len(w) >= 1
                warning_found = False
                for warning in w:
                    if "duplicate" in str(warning.message).lower() and "--test" in str(warning.message):
                        warning_found = True
                        break
                assert warning_found, f"Expected duplicate option warning, got: {[str(warning.message) for warning in w]}"
            else:
                # No warnings in release mode
                pass
    
    def test_get_params_with_custom_params_and_help(self):
        """Test get_params with custom parameters and help option."""
        ctx = Context(Command('test'))
        
        # Create command with custom parameters
        opt1 = Option(['--verbose', '-v'])
        opt2 = Option(['--file', '-f'])
        
        cmd = Command('test', params=[opt1, opt2], add_help_option=True)
        
        params = cmd.get_params(ctx)
        
        # Should have 3 parameters (2 custom + help)
        assert len(params) == 3
        # Verify our custom parameters are included
        param_opts = [opt for param in params for opt in param.opts]
        assert '--verbose' in param_opts
        assert '-v' in param_opts
        assert '--file' in param_opts
        assert '-f' in param_opts
        assert '--help' in param_opts
    
    def test_get_params_empty_command(self):
        """Test get_params with empty command (no custom params)."""
        ctx = Context(Command('test'))
        cmd = Command('test', params=[], add_help_option=True)
        
        params = cmd.get_params(ctx)
        
        # Should only have help option
        assert len(params) == 1
        assert '--help' in params[0].opts
    
    def test_get_params_multiple_duplicate_opts(self):
        """Test get_params with multiple duplicate options."""
        ctx = Context(Command('test'))
        
        # Create command with multiple duplicate options
        opt1 = Option(['--verbose', '-v'])
        opt2 = Option(['--verbose'])  # Duplicate long option
        opt3 = Option(['-v'])  # Duplicate short option
        
        cmd = Command('test', params=[opt1, opt2, opt3], add_help_option=False)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            params = cmd.get_params(ctx)
            
            # Check if warnings were raised (depends on __debug__)
            if __debug__:
                # Should have warnings for duplicates
                assert len(w) >= 1
                warning_messages = [str(warning.message) for warning in w]
                verbose_warning = any('--verbose' in msg for msg in warning_messages)
                v_warning = any('-v' in msg for msg in warning_messages)
                assert verbose_warning or v_warning, f"Expected duplicate option warnings, got: {warning_messages}"
            else:
                # No warnings in release mode
                pass
    
    def test_get_params_no_duplicates(self):
        """Test get_params with no duplicate options."""
        ctx = Context(Command('test'))
        
        # Create command with unique options
        opt1 = Option(['--verbose', '-v'])
        opt2 = Option(['--file', '-f'])
        
        cmd = Command('test', params=[opt1, opt2], add_help_option=False)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            params = cmd.get_params(ctx)
            
            # Should not have any warnings about duplicates
            duplicate_warnings = [warning for warning in w if "duplicate" in str(warning.message).lower()]
            assert len(duplicate_warnings) == 0
    
    def test_get_params_with_help_option_disabled(self):
        """Test get_params when help option is explicitly disabled."""
        ctx = Context(Command('test'))
        cmd = Command('test', add_help_option=False)
        
        params = cmd.get_params(ctx)
        
        # Should not have help option
        assert len(params) == 0
    
    def test_get_params_with_existing_params_and_help(self):
        """Test get_params with existing params and help option enabled."""
        ctx = Context(Command('test'))
        
        # Create command with existing parameters
        opt1 = Option(['--test'])
        cmd = Command('test', params=[opt1], add_help_option=True)
        
        params = cmd.get_params(ctx)
        
        # Should have both the test option and help option
        assert len(params) == 2
        param_opts = [opt for param in params for opt in param.opts]
        assert '--test' in param_opts
        assert '--help' in param_opts
