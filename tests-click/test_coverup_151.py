# file: src/click/src/click/types.py:288-306
# asked: {"lines": [288, 298, 300, 301, 303, 304, 306], "branches": [[300, 301], [300, 303], [303, 304], [303, 306]]}
# gained: {"lines": [288, 298, 300, 301, 303, 304, 306], "branches": [[300, 301], [300, 303], [303, 304], [303, 306]]}

import pytest
import enum
from click.types import Choice
from click.core import Context, Command


class TestEnum(enum.Enum):
    OPTION_A = "value_a"
    OPTION_B = "value_b"


def test_normalize_choice_with_enum_and_ctx_token_normalize_func():
    """Test normalize_choice with enum choice and context token_normalize_func."""
    choice_type = Choice(["value_a", "value_b"])
    command = Command("test")
    ctx = Context(command)
    ctx.token_normalize_func = lambda x: x.upper()
    
    result = choice_type.normalize_choice(TestEnum.OPTION_A, ctx)
    assert result == "OPTION_A"


def test_normalize_choice_with_string_and_ctx_token_normalize_func():
    """Test normalize_choice with string choice and context token_normalize_func."""
    choice_type = Choice(["value_a", "value_b"])
    command = Command("test")
    ctx = Context(command)
    ctx.token_normalize_func = lambda x: x.upper()
    
    result = choice_type.normalize_choice("value_a", ctx)
    assert result == "VALUE_A"


def test_normalize_choice_with_enum_and_case_insensitive():
    """Test normalize_choice with enum choice and case insensitive."""
    choice_type = Choice(["option_a", "option_b"], case_sensitive=False)
    
    result = choice_type.normalize_choice(TestEnum.OPTION_A, None)
    assert result == "option_a"


def test_normalize_choice_with_string_and_case_insensitive():
    """Test normalize_choice with string choice and case insensitive."""
    choice_type = Choice(["option_a", "option_b"], case_sensitive=False)
    
    result = choice_type.normalize_choice("OPTION_A", None)
    assert result == "option_a"


def test_normalize_choice_with_enum_and_ctx_token_normalize_func_and_case_insensitive():
    """Test normalize_choice with enum choice, context token_normalize_func, and case insensitive."""
    choice_type = Choice(["option_a", "option_b"], case_sensitive=False)
    command = Command("test")
    ctx = Context(command)
    ctx.token_normalize_func = lambda x: x.upper()
    
    result = choice_type.normalize_choice(TestEnum.OPTION_A, ctx)
    assert result == "option_a"


def test_normalize_choice_with_string_and_ctx_token_normalize_func_and_case_insensitive():
    """Test normalize_choice with string choice, context token_normalize_func, and case insensitive."""
    choice_type = Choice(["option_a", "option_b"], case_sensitive=False)
    command = Command("test")
    ctx = Context(command)
    ctx.token_normalize_func = lambda x: x.upper()
    
    result = choice_type.normalize_choice("Option_A", ctx)
    assert result == "option_a"


def test_normalize_choice_with_enum_no_ctx_no_case_insensitive():
    """Test normalize_choice with enum choice, no context, and case sensitive."""
    choice_type = Choice(["OPTION_A", "OPTION_B"], case_sensitive=True)
    
    result = choice_type.normalize_choice(TestEnum.OPTION_A, None)
    assert result == "OPTION_A"


def test_normalize_choice_with_string_no_ctx_no_case_insensitive():
    """Test normalize_choice with string choice, no context, and case sensitive."""
    choice_type = Choice(["OPTION_A", "OPTION_B"], case_sensitive=True)
    
    result = choice_type.normalize_choice("OPTION_A", None)
    assert result == "OPTION_A"
