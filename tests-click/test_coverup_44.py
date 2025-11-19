# file: src/click/src/click/parser.py:502-532
# asked: {"lines": [502, 503, 505, 513, 514, 516, 517, 519, 521, 522, 524, 525, 527, 528, 530, 532], "branches": [[505, 513], [505, 521], [521, 522], [521, 532]]}
# gained: {"lines": [502, 503, 505, 513, 514, 516, 517, 519, 521, 522, 524, 525, 527, 528, 530, 532], "branches": [[505, 513], [505, 521], [521, 522], [521, 532]]}

import pytest
import warnings
import click.parser


def test_getattr_deprecated_parser_classes():
    """Test accessing deprecated parser classes triggers warning and returns correct object."""
    with pytest.warns(DeprecationWarning, match="'parser.OptionParser' is deprecated"):
        result = click.parser.OptionParser
        assert result is not None
        assert hasattr(result, '__name__')


def test_getattr_deprecated_parser_argument():
    """Test accessing deprecated Argument class triggers warning and returns correct object."""
    with pytest.warns(DeprecationWarning, match="'parser.Argument' is deprecated"):
        result = click.parser.Argument
        assert result is not None
        assert hasattr(result, '__name__')


def test_getattr_deprecated_parser_option():
    """Test accessing deprecated Option class triggers warning and returns correct object."""
    with pytest.warns(DeprecationWarning, match="'parser.Option' is deprecated"):
        result = click.parser.Option
        assert result is not None
        assert hasattr(result, '__name__')


def test_getattr_deprecated_split_opt():
    """Test accessing deprecated split_opt function triggers warning and returns correct object."""
    with pytest.warns(DeprecationWarning, match="'parser.split_opt' is deprecated"):
        result = click.parser.split_opt
        assert result is not None
        assert callable(result)


def test_getattr_deprecated_normalize_opt():
    """Test accessing deprecated normalize_opt function triggers warning and returns correct object."""
    with pytest.warns(DeprecationWarning, match="'parser.normalize_opt' is deprecated"):
        result = click.parser.normalize_opt
        assert result is not None
        assert callable(result)


def test_getattr_deprecated_parsing_state():
    """Test accessing deprecated ParsingState class triggers warning and returns correct object."""
    with pytest.warns(DeprecationWarning, match="'parser.ParsingState' is deprecated"):
        result = click.parser.ParsingState
        assert result is not None
        assert hasattr(result, '__name__')


def test_getattr_deprecated_split_arg_string():
    """Test accessing deprecated split_arg_string function triggers warning and returns correct object."""
    with pytest.warns(DeprecationWarning, match="Importing 'parser.split_arg_string' is deprecated"):
        result = click.parser.split_arg_string
        assert result is not None
        assert callable(result)


def test_getattr_unknown_attribute():
    """Test accessing unknown attribute raises AttributeError."""
    with pytest.raises(AttributeError, match="unknown_attribute"):
        _ = click.parser.unknown_attribute
