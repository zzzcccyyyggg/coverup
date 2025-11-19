# file: src/click/src/click/formatting.py:147-183
# asked: {"lines": [147, 155, 156, 158, 159, 161, 163, 164, 165, 166, 167, 168, 169, 174, 175, 176, 177, 178, 179, 183], "branches": [[155, 156], [155, 158], [161, 163], [161, 174]]}
# gained: {"lines": [147, 155, 156, 158, 159, 161, 163, 164, 165, 166, 167, 168, 169, 174, 175, 176, 177, 178, 179, 183], "branches": [[155, 156], [155, 158], [161, 163], [161, 174]]}

import pytest
from click.formatting import HelpFormatter, wrap_text
from click._compat import term_len
from gettext import gettext as _

class TestHelpFormatterWriteUsage:
    def test_write_usage_long_prefix_fits_args_on_same_line(self):
        """Test when usage prefix fits with args on same line (lines 161-169)"""
        formatter = HelpFormatter(width=100, max_width=100)
        formatter.current_indent = 4
        prog = "myprogram"
        args = "arg1 arg2 arg3"
        prefix = "Usage: "
        
        formatter.write_usage(prog, args, prefix)
        
        result = formatter.getvalue()
        expected_prefix = f"{prefix:>{formatter.current_indent}}{prog} "
        expected_indent = " " * term_len(expected_prefix)
        expected_text = wrap_text(
            args,
            formatter.width - formatter.current_indent,
            initial_indent=expected_prefix,
            subsequent_indent=expected_indent
        )
        assert result == expected_text + "\n"
    
    def test_write_usage_long_prefix_args_on_next_line(self):
        """Test when prefix is too long, args go on next line (lines 174-182)"""
        formatter = HelpFormatter(width=40, max_width=40)
        formatter.current_indent = 4
        prog = "verylongprogramnamethatmakestheprefixverylong"
        args = "arg1 arg2 arg3 arg4 arg5 arg6 arg7"
        prefix = "Usage: "
        
        formatter.write_usage(prog, args, prefix)
        
        result = formatter.getvalue()
        usage_prefix = f"{prefix:>{formatter.current_indent}}{prog} "
        indent = " " * (max(formatter.current_indent, term_len(prefix)) + 4)
        expected_text = usage_prefix + "\n" + wrap_text(
            args, 
            formatter.width - formatter.current_indent,
            initial_indent=indent,
            subsequent_indent=indent
        )
        assert result == expected_text + "\n"
    
    def test_write_usage_default_prefix(self):
        """Test when prefix is None, uses default translated prefix (line 156)"""
        formatter = HelpFormatter(width=100, max_width=100)
        formatter.current_indent = 2
        prog = "testprog"
        args = "arg1 arg2"
        
        formatter.write_usage(prog, args)
        
        result = formatter.getvalue()
        default_prefix = f"{_('Usage:')} "
        usage_prefix = f"{default_prefix:>{formatter.current_indent}}{prog} "
        expected_indent = " " * term_len(usage_prefix)
        expected_text = wrap_text(
            args,
            formatter.width - formatter.current_indent,
            initial_indent=usage_prefix,
            subsequent_indent=expected_indent
        )
        assert result == expected_text + "\n"
    
    def test_write_usage_empty_args(self):
        """Test with empty args string"""
        formatter = HelpFormatter(width=100, max_width=100)
        formatter.current_indent = 4
        prog = "program"
        args = ""
        prefix = "Usage: "
        
        formatter.write_usage(prog, args, prefix)
        
        result = formatter.getvalue()
        usage_prefix = f"{prefix:>{formatter.current_indent}}{prog} "
        expected_indent = " " * term_len(usage_prefix)
        expected_text = wrap_text(
            args,
            formatter.width - formatter.current_indent,
            initial_indent=usage_prefix,
            subsequent_indent=expected_indent
        )
        assert result == expected_text + "\n"
    
    def test_write_usage_narrow_terminal_long_program(self):
        """Test edge case with very narrow terminal and long program name"""
        formatter = HelpFormatter(width=30, max_width=30)
        formatter.current_indent = 2
        prog = "extremelylongprogramnamethatexceedswidth"
        args = "arg1 arg2 arg3"
        prefix = "Usage: "
        
        formatter.write_usage(prog, args, prefix)
        
        result = formatter.getvalue()
        usage_prefix = f"{prefix:>{formatter.current_indent}}{prog} "
        indent = " " * (max(formatter.current_indent, term_len(prefix)) + 4)
        expected_text = usage_prefix + "\n" + wrap_text(
            args, 
            formatter.width - formatter.current_indent,
            initial_indent=indent,
            subsequent_indent=indent
        )
        assert result == expected_text + "\n"
