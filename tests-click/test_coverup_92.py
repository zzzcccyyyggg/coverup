# file: src/click/src/click/parser.py:237-259
# asked: {"lines": [237, 240, 245, 250, 252, 253, 254, 256, 257, 258, 259], "branches": [[252, 253], [252, 256]]}
# gained: {"lines": [237, 240, 245, 250, 252, 253, 254, 256, 257, 258, 259], "branches": [[252, 253], [252, 256]]}

import pytest
from click.core import Context, Command
from click.parser import _OptionParser

class TestOptionParserInit:
    def test_init_without_ctx(self):
        """Test _OptionParser.__init__ without a Context."""
        parser = _OptionParser()
        assert parser.ctx is None
        assert parser.allow_interspersed_args is True
        assert parser.ignore_unknown_options is False
        assert parser._short_opt == {}
        assert parser._long_opt == {}
        assert parser._opt_prefixes == {"-", "--"}
        assert parser._args == []

    def test_init_with_ctx_default_values(self):
        """Test _OptionParser.__init__ with a Context using default values."""
        cmd = Command("test_cmd")
        ctx = Context(cmd)
        parser = _OptionParser(ctx)
        assert parser.ctx is ctx
        assert parser.allow_interspersed_args is True
        assert parser.ignore_unknown_options is False
        assert parser._short_opt == {}
        assert parser._long_opt == {}
        assert parser._opt_prefixes == {"-", "--"}
        assert parser._args == []

    def test_init_with_ctx_custom_allow_interspersed_args(self):
        """Test _OptionParser.__init__ with a Context with custom allow_interspersed_args."""
        cmd = Command("test_cmd")
        ctx = Context(cmd, allow_interspersed_args=False)
        parser = _OptionParser(ctx)
        assert parser.ctx is ctx
        assert parser.allow_interspersed_args is False
        assert parser.ignore_unknown_options is False
        assert parser._short_opt == {}
        assert parser._long_opt == {}
        assert parser._opt_prefixes == {"-", "--"}
        assert parser._args == []

    def test_init_with_ctx_custom_ignore_unknown_options(self):
        """Test _OptionParser.__init__ with a Context with custom ignore_unknown_options."""
        cmd = Command("test_cmd")
        ctx = Context(cmd, ignore_unknown_options=True)
        parser = _OptionParser(ctx)
        assert parser.ctx is ctx
        assert parser.allow_interspersed_args is True
        assert parser.ignore_unknown_options is True
        assert parser._short_opt == {}
        assert parser._long_opt == {}
        assert parser._opt_prefixes == {"-", "--"}
        assert parser._args == []

    def test_init_with_ctx_both_custom_values(self):
        """Test _OptionParser.__init__ with a Context with both custom values."""
        cmd = Command("test_cmd")
        ctx = Context(cmd, allow_interspersed_args=False, ignore_unknown_options=True)
        parser = _OptionParser(ctx)
        assert parser.ctx is ctx
        assert parser.allow_interspersed_args is False
        assert parser.ignore_unknown_options is True
        assert parser._short_opt == {}
        assert parser._long_opt == {}
        assert parser._opt_prefixes == {"-", "--"}
        assert parser._args == []
