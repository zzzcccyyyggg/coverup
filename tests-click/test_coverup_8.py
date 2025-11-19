# file: src/click/src/click/parser.py:128-159
# asked: {"lines": [128, 133, 134, 135, 137, 138, 139, 141, 142, 143, 144, 145, 146, 147, 149, 150, 152, 153, 155, 156, 157, 158, 159], "branches": [[141, 142], [141, 152], [143, 144], [143, 145], [146, 147], [146, 149], [152, 153], [152, 155]]}
# gained: {"lines": [128, 133, 134, 135, 137, 138, 139, 141, 142, 143, 144, 145, 146, 147, 149, 150, 152, 153, 155, 156, 157, 158, 159], "branches": [[141, 142], [141, 152], [143, 144], [143, 145], [146, 147], [146, 149], [152, 153], [152, 155]]}

import pytest
from click.core import Option as CoreOption
from click.parser import _Option, _split_opt


class TestOption:
    def test_init_with_invalid_option_start_character(self):
        """Test that ValueError is raised when option has invalid start character."""
        obj = CoreOption(['--test'], 'test')
        with pytest.raises(ValueError, match="Invalid start character for option"):
            _Option(obj, ['invalid'], 'dest')

    def test_init_with_single_char_short_option(self):
        """Test initialization with single character short option."""
        obj = CoreOption(['-a'], 'a')
        option = _Option(obj, ['-a'], 'a_dest')
        assert option._short_opts == ['-a']
        assert option._long_opts == []
        assert option.prefixes == {'-'}

    def test_init_with_multi_char_short_option(self):
        """Test initialization with multi-character short option."""
        obj = CoreOption(['-ab'], 'ab')
        option = _Option(obj, ['-ab'], 'ab_dest')
        # Multi-character options starting with single dash are treated as long options
        assert option._short_opts == []
        assert option._long_opts == ['-ab']
        assert option.prefixes == {'-'}

    def test_init_with_long_option_single_dash(self):
        """Test initialization with long option using single dash."""
        obj = CoreOption(['-test'], 'test')
        option = _Option(obj, ['-test'], 'test_dest')
        assert option._short_opts == []
        assert option._long_opts == ['-test']
        assert option.prefixes == {'-'}

    def test_init_with_long_option_double_dash(self):
        """Test initialization with long option using double dash."""
        obj = CoreOption(['--test'], 'test')
        option = _Option(obj, ['--test'], 'test_dest')
        assert option._short_opts == []
        assert option._long_opts == ['--test']
        assert option.prefixes == {'--', '-'}

    def test_init_with_mixed_options(self):
        """Test initialization with mixed short and long options."""
        obj = CoreOption(['-a', '--all'], 'all')
        option = _Option(obj, ['-a', '--all'], 'all_dest')
        assert option._short_opts == ['-a']
        assert option._long_opts == ['--all']
        assert option.prefixes == {'-', '--'}

    def test_init_with_action_none_sets_store(self):
        """Test that action defaults to 'store' when None is provided."""
        obj = CoreOption(['--test'], 'test')
        option = _Option(obj, ['--test'], 'test_dest', action=None)
        assert option.action == 'store'

    def test_init_with_explicit_action(self):
        """Test initialization with explicit action parameter."""
        obj = CoreOption(['--test'], 'test')
        option = _Option(obj, ['--test'], 'test_dest', action='append')
        assert option.action == 'append'

    def test_init_with_nargs_and_const(self):
        """Test initialization with custom nargs and const values."""
        obj = CoreOption(['--test'], 'test')
        option = _Option(obj, ['--test'], 'test_dest', nargs=2, const='default')
        assert option.nargs == 2
        assert option.const == 'default'

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters specified."""
        obj = CoreOption(['-v', '--verbose'], 'verbose')
        option = _Option(
            obj, 
            ['-v', '--verbose'], 
            'verbose_dest', 
            action='count', 
            nargs=0, 
            const=1
        )
        assert option._short_opts == ['-v']
        assert option._long_opts == ['--verbose']
        assert option.prefixes == {'-', '--'}
        assert option.dest == 'verbose_dest'
        assert option.action == 'count'
        assert option.nargs == 0
        assert option.const == 1
        assert option.obj == obj
