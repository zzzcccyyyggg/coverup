# file: src/click/src/click/termui.py:60-73
# asked: {"lines": [60, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73], "branches": [[69, 70], [69, 71], [71, 72], [71, 73]]}
# gained: {"lines": [60, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73], "branches": [[69, 70], [69, 71], [71, 72], [71, 73]]}

import pytest
import typing as t
from click.types import Choice, ParamType
from click.termui import _build_prompt, _format_default


class TestBuildPrompt:
    """Test cases for _build_prompt function to achieve full coverage."""
    
    def test_build_prompt_with_choice_type_and_show_choices(self):
        """Test _build_prompt with Choice type and show_choices=True."""
        choice_type = Choice(['option1', 'option2', 'option3'])
        result = _build_prompt(
            text="Choose an option",
            suffix=": ",
            show_default=False,
            default=None,
            show_choices=True,
            type=choice_type
        )
        expected = "Choose an option (option1, option2, option3): "
        assert result == expected
    
    def test_build_prompt_with_choice_type_and_hide_choices(self):
        """Test _build_prompt with Choice type but show_choices=False."""
        choice_type = Choice(['option1', 'option2'])
        result = _build_prompt(
            text="Choose an option",
            suffix=": ",
            show_default=False,
            default=None,
            show_choices=False,
            type=choice_type
        )
        expected = "Choose an option: "
        assert result == expected
    
    def test_build_prompt_with_non_choice_type_and_show_choices(self):
        """Test _build_prompt with non-Choice type and show_choices=True."""
        class CustomType(ParamType):
            name = "custom"
        
        custom_type = CustomType()
        result = _build_prompt(
            text="Enter value",
            suffix=": ",
            show_default=False,
            default=None,
            show_choices=True,
            type=custom_type
        )
        expected = "Enter value: "
        assert result == expected
    
    def test_build_prompt_with_default_and_show_default(self):
        """Test _build_prompt with default value and show_default=True."""
        result = _build_prompt(
            text="Enter name",
            suffix=": ",
            show_default=True,
            default="John Doe",
            show_choices=True,
            type=None
        )
        expected = "Enter name [John Doe]: "
        assert result == expected
    
    def test_build_prompt_with_default_and_hide_default(self):
        """Test _build_prompt with default value but show_default=False."""
        result = _build_prompt(
            text="Enter name",
            suffix=": ",
            show_default=False,
            default="John Doe",
            show_choices=True,
            type=None
        )
        expected = "Enter name: "
        assert result == expected
    
    def test_build_prompt_with_choice_type_default_and_show_default(self):
        """Test _build_prompt with Choice type, default value, and show_default=True."""
        choice_type = Choice(['yes', 'no', 'maybe'])
        result = _build_prompt(
            text="Make a choice",
            suffix="? ",
            show_default=True,
            default="yes",
            show_choices=True,
            type=choice_type
        )
        expected = "Make a choice (yes, no, maybe) [yes]? "
        assert result == expected
    
    def test_build_prompt_with_numeric_choices(self):
        """Test _build_prompt with numeric choices in Choice type."""
        choice_type = Choice([1, 2, 3])
        result = _build_prompt(
            text="Select number",
            suffix=": ",
            show_default=False,
            default=None,
            show_choices=True,
            type=choice_type
        )
        expected = "Select number (1, 2, 3): "
        assert result == expected
    
    def test_build_prompt_empty_suffix(self):
        """Test _build_prompt with empty suffix."""
        choice_type = Choice(['a', 'b'])
        result = _build_prompt(
            text="Choose",
            suffix="",
            show_default=True,
            default="a",
            show_choices=True,
            type=choice_type
        )
        expected = "Choose (a, b) [a]"
        assert result == expected
