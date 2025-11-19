# file: src/click/src/click/formatting.py:283-301
# asked: {"lines": [283, 289, 290, 292, 293, 295, 296, 298, 300, 301], "branches": [[292, 293], [292, 300], [295, 296], [295, 298]]}
# gained: {"lines": [283, 289, 290, 292, 293, 295, 296, 298, 300, 301], "branches": [[292, 293], [292, 300], [295, 296], [295, 298]]}

import pytest
from click.formatting import join_options


class TestJoinOptions:
    def test_join_options_no_slash_prefix(self):
        """Test join_options with options that don't have slash prefix."""
        options = ["-a", "--long", "-b"]
        result, has_slash = join_options(options)
        assert result == "-a, -b, --long"
        assert has_slash is False

    def test_join_options_with_slash_prefix(self):
        """Test join_options with options that have slash prefix."""
        options = ["/a", "/b", "--long"]
        result, has_slash = join_options(options)
        assert result == "/a, /b, --long"
        assert has_slash is True

    def test_join_options_mixed_prefixes(self):
        """Test join_options with mixed prefix types including slash."""
        options = ["-a", "/b", "--long", "/c"]
        result, has_slash = join_options(options)
        assert result == "-a, /b, /c, --long"
        assert has_slash is True

    def test_join_options_single_slash_prefix(self):
        """Test join_options with only one slash prefix option."""
        options = ["-a", "--long", "/b"]
        result, has_slash = join_options(options)
        assert result == "-a, /b, --long"
        assert has_slash is True

    def test_join_options_empty_list(self):
        """Test join_options with empty options list."""
        options = []
        result, has_slash = join_options(options)
        assert result == ""
        assert has_slash is False

    def test_join_options_single_option_no_slash(self):
        """Test join_options with single option without slash."""
        options = ["--help"]
        result, has_slash = join_options(options)
        assert result == "--help"
        assert has_slash is False

    def test_join_options_single_option_with_slash(self):
        """Test join_options with single option with slash."""
        options = ["/help"]
        result, has_slash = join_options(options)
        assert result == "/help"
        assert has_slash is True
