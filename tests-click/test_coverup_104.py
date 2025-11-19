# file: src/click/src/click/termui.py:293-310
# asked: {"lines": [293, 294, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310], "branches": []}
# gained: {"lines": [293, 294, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309], "branches": []}

import pytest
import typing as t
from click.termui import progressbar
from click._termui_impl import ProgressBar
from io import StringIO


def test_progressbar_overload_parameters():
    """Test that progressbar can be called with all overload signature parameters."""
    # Test that we can call progressbar with all the parameters from the overload
    with progressbar(
        length=10,
        label="Test",
        hidden=False,
        show_eta=True,
        show_percent=None,
        show_pos=False,
        fill_char="#",
        empty_char="-",
        bar_template="%(label)s  [%(bar)s]  %(info)s",
        info_sep="  ",
        width=36,
        file=None,
        color=None,
        update_min_steps=1
    ) as bar:
        assert isinstance(bar, ProgressBar)
        assert bar.length == 10
        assert bar.label == "Test"
        assert bar.hidden is False
        assert bar.show_eta is True
        assert bar.show_percent is None
        assert bar.show_pos is False
        assert bar.fill_char == "#"
        assert bar.empty_char == "-"
        assert bar.bar_template == "%(label)s  [%(bar)s]  %(info)s"
        assert bar.info_sep == "  "
        assert bar.width == 36
        assert bar.update_min_steps == 1


def test_progressbar_with_all_overload_parameters_custom_values():
    """Test progressbar with all parameters from the overload signature using custom values."""
    output = StringIO()
    
    with progressbar(
        length=100,
        label="Custom Progress",
        hidden=True,
        show_eta=False,
        show_percent=False,
        show_pos=True,
        fill_char="=",
        empty_char=".",
        bar_template="[%(bar)s] %(info)s",
        info_sep=" | ",
        width=50,
        file=output,
        color=False,
        update_min_steps=5
    ) as bar:
        assert isinstance(bar, ProgressBar)
        assert bar.length == 100
        assert bar.label == "Custom Progress"
        assert bar.hidden is True
        assert bar.show_eta is False
        assert bar.show_percent is False
        assert bar.show_pos is True
        assert bar.fill_char == "="
        assert bar.empty_char == "."
        assert bar.bar_template == "[%(bar)s] %(info)s"
        assert bar.info_sep == " | "
        assert bar.width == 50
        assert bar.color is False
        assert bar.update_min_steps == 5


def test_progressbar_hidden_progress():
    """Test progressbar with hidden=True parameter."""
    output = StringIO()
    
    with progressbar(length=50, hidden=True, file=output) as bar:
        bar.update(10)
        bar.update(20)
    
    # The output should be empty when hidden=True
    assert output.getvalue() == ""


def test_progressbar_with_show_percent_none():
    """Test progressbar with show_percent=None parameter."""
    output = StringIO()
    
    with progressbar(length=25, show_percent=None, file=output) as bar:
        # When show_percent=None, it should remain None in the ProgressBar instance
        assert bar.show_percent is None


def test_progressbar_with_show_percent_false():
    """Test progressbar with show_percent=False parameter."""
    output = StringIO()
    
    with progressbar(length=25, show_percent=False, file=output) as bar:
        assert bar.show_percent is False


def test_progressbar_with_custom_file():
    """Test progressbar with custom file parameter."""
    custom_file = StringIO()
    
    with progressbar(length=30, file=custom_file) as bar:
        bar.update(15)
    
    # Verify that output was written to the custom file
    output_content = custom_file.getvalue()
    assert len(output_content) > 0


def test_progressbar_with_color_parameter():
    """Test progressbar with color parameter."""
    output = StringIO()
    
    # Test with color=True
    with progressbar(length=20, color=True, file=output) as bar:
        assert bar.color is True
    
    output = StringIO()
    
    # Test with color=False  
    with progressbar(length=20, color=False, file=output) as bar:
        assert bar.color is False


def test_progressbar_update_min_steps():
    """Test progressbar with custom update_min_steps parameter."""
    output = StringIO()
    
    with progressbar(length=100, update_min_steps=10, file=output) as bar:
        assert bar.update_min_steps == 10
        
        # Test that the ProgressBar instance has the correct update_min_steps value
        # The actual rendering behavior might be complex, but we can verify the parameter is set
        bar.update(5)
        bar.update(10)
        # The test passes if we can set the parameter and use the progressbar without errors


def test_progressbar_with_minimal_parameters():
    """Test progressbar with only the required length parameter."""
    with progressbar(length=5) as bar:
        assert isinstance(bar, ProgressBar)
        assert bar.length == 5
        # Verify default values from the overload signature
        assert bar.label == ""
        assert bar.hidden is False
        assert bar.show_eta is True
        assert bar.show_percent is None
        assert bar.show_pos is False
        assert bar.fill_char == "#"
        assert bar.empty_char == "-"
        assert bar.bar_template == "%(label)s  [%(bar)s]  %(info)s"
        assert bar.info_sep == "  "
        assert bar.width == 36
        assert bar.update_min_steps == 1
