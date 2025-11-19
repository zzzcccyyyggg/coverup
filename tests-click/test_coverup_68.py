# file: src/click/src/click/parser.py:469-499
# asked: {"lines": [469, 470, 474, 475, 477, 478, 483, 484, 485, 492, 493, 494, 496, 497, 499], "branches": [[474, 475], [474, 477], [492, 493], [492, 496], [496, 497], [496, 499]]}
# gained: {"lines": [469, 470, 474, 475, 477, 478, 483, 484, 485, 492, 493, 494, 496, 497, 499], "branches": [[474, 475], [474, 477], [492, 493], [492, 496], [496, 497], [496, 499]]}

import pytest
from unittest.mock import Mock
from click.parser import _OptionParser, _ParsingState
from click.exceptions import NoSuchOption


class TestOptionParserProcessOpts:
    """Test cases for _OptionParser._process_opts method to achieve full coverage."""
    
    def test_process_opts_with_explicit_value_and_long_opt_match(self, monkeypatch):
        """Test line 474-485: long option with explicit value that matches."""
        parser = _OptionParser()
        state = _ParsingState([])
        
        # Mock _match_long_opt to not raise NoSuchOption
        mock_match_long_opt = Mock()
        monkeypatch.setattr(parser, '_match_long_opt', mock_match_long_opt)
        
        # Call with explicit value (line 474-475)
        parser._process_opts("--option=value", state)
        
        # Verify _match_long_opt was called with correct arguments
        mock_match_long_opt.assert_called_once()
        call_args = mock_match_long_opt.call_args[0]
        assert call_args[0] == "--option"  # normalized long option
        assert call_args[1] == "value"  # explicit value
        assert call_args[2] is state
    
    def test_process_opts_without_explicit_value_and_long_opt_match(self, monkeypatch):
        """Test line 477-485: long option without explicit value that matches."""
        parser = _OptionParser()
        state = _ParsingState([])
        
        # Mock _match_long_opt to not raise NoSuchOption
        mock_match_long_opt = Mock()
        monkeypatch.setattr(parser, '_match_long_opt', mock_match_long_opt)
        
        # Call without explicit value (line 477)
        parser._process_opts("--option", state)
        
        # Verify _match_long_opt was called with correct arguments
        mock_match_long_opt.assert_called_once()
        call_args = mock_match_long_opt.call_args[0]
        assert call_args[0] == "--option"  # normalized long option
        assert call_args[1] is None  # no explicit value
        assert call_args[2] is state
    
    def test_process_opts_long_opt_fails_short_prefix_falls_to_short_opt(self, monkeypatch):
        """Test line 483-494: long option fails, short prefix, falls to short option matching."""
        parser = _OptionParser()
        state = _ParsingState([])
        
        # Mock _match_long_opt to raise NoSuchOption
        def mock_match_long_opt(opt, explicit_value, state):
            raise NoSuchOption("Option not found")
        monkeypatch.setattr(parser, '_match_long_opt', mock_match_long_opt)
        
        # Mock _match_short_opt to verify it's called
        mock_short_opt = Mock()
        monkeypatch.setattr(parser, '_match_short_opt', mock_short_opt)
        
        # Call with short prefix (line 492-493)
        parser._process_opts("-o", state)
        
        # Verify _match_short_opt was called
        mock_short_opt.assert_called_once_with("-o", state)
    
    def test_process_opts_long_opt_fails_long_prefix_ignore_unknown_false_raises(self):
        """Test line 483-497: long option fails, long prefix, ignore_unknown_options=False raises."""
        parser = _OptionParser()
        parser.ignore_unknown_options = False
        state = _ParsingState([])
        
        # Should raise NoSuchOption (line 497)
        with pytest.raises(NoSuchOption):
            parser._process_opts("--unknown", state)
    
    def test_process_opts_long_opt_fails_long_prefix_ignore_unknown_true_appends(self):
        """Test line 483-499: long option fails, long prefix, ignore_unknown_options=True appends to largs."""
        parser = _OptionParser()
        parser.ignore_unknown_options = True
        state = _ParsingState([])
        
        # Call with long prefix and ignore_unknown_options=True (line 499)
        parser._process_opts("--unknown", state)
        
        # Verify arg was appended to largs
        assert state.largs == ["--unknown"]
    
    def test_process_opts_with_normalization(self, monkeypatch):
        """Test line 478: normalization of long option with context."""
        from click.core import Context
        
        # Create a minimal mock command for Context
        mock_command = Mock()
        mock_command.allow_extra_args = False
        mock_command.allow_interspersed_args = True
        mock_command.ignore_unknown_options = False
        
        ctx = Context(mock_command)
        parser = _OptionParser(ctx)
        state = _ParsingState([])
        
        # Mock _match_long_opt to verify normalized option
        def mock_match_long_opt(opt, explicit_value, state):
            assert opt == "--option"  # Should be normalized
            
        monkeypatch.setattr(parser, '_match_long_opt', mock_match_long_opt)
        
        # Call with option that would be normalized
        parser._process_opts("--option", state)
