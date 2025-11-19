# file: src/click/src/click/termui.py:313-331
# asked: {"lines": [313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331], "branches": []}
# gained: {"lines": [313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330], "branches": []}

import pytest
import io
from click import progressbar
from click._termui_impl import ProgressBar


def test_progressbar_overload_with_iterable_and_length():
    """Test the progressbar overload with both iterable and length parameters."""
    # This should call the overloaded signature
    with progressbar(range(5), length=5) as bar:
        assert isinstance(bar, ProgressBar)
        assert bar.length == 5


def test_progressbar_overload_with_all_parameters():
    """Test the progressbar overload with all parameters to cover lines 313-331."""
    iterable = [1, 2, 3, 4, 5]
    output = io.StringIO()
    
    with progressbar(
        iterable=iterable,
        length=5,
        label="Test Progress",
        hidden=False,
        show_eta=True,
        show_percent=True,
        show_pos=True,
        item_show_func=lambda x: f"Item {x}" if x else None,
        fill_char="=",
        empty_char=".",
        bar_template="%(label)s [%(bar)s] %(info)s",
        info_sep=" | ",
        width=40,
        file=output,
        color=None,
        update_min_steps=2
    ) as bar:
        assert isinstance(bar, ProgressBar)
        assert bar.length == 5
        assert bar.label == "Test Progress"
        assert bar.hidden is False
        assert bar.show_eta is True
        assert bar.show_percent is True
        assert bar.show_pos is True
        assert bar.fill_char == "="
        assert bar.empty_char == "."
        assert bar.bar_template == "%(label)s [%(bar)s] %(info)s"
        assert bar.info_sep == " | "
        assert bar.width == 40
        assert bar.file is output
        assert bar.color is None
        assert bar.update_min_steps == 2
        
        # Iterate through to trigger progress updates
        for item in bar:
            assert item in iterable


def test_progressbar_overload_with_none_iterable_and_length():
    """Test the progressbar overload with None iterable but with length."""
    output = io.StringIO()
    
    with progressbar(
        iterable=None,
        length=10,
        label="Counting",
        file=output
    ) as bar:
        assert isinstance(bar, ProgressBar)
        assert bar.length == 10
        assert bar.label == "Counting"
        
        # Should be able to iterate through the generated range
        items = list(bar)
        assert len(items) == 10
        assert items == list(range(10))


def test_progressbar_overload_with_custom_item_show_func():
    """Test the progressbar overload with custom item_show_func."""
    
    def custom_show_func(item):
        return f"Processing: {item}" if item is not None else "Done"
    
    with progressbar(
        range(3),
        length=3,
        item_show_func=custom_show_func
    ) as bar:
        assert bar.item_show_func is custom_show_func
        
        for item in bar:
            assert item in [0, 1, 2]


def test_progressbar_overload_with_hidden_true():
    """Test the progressbar overload with hidden=True."""
    with progressbar(
        range(5),
        length=5,
        hidden=True
    ) as bar:
        assert bar.hidden is True
        # Even though hidden, should still function normally
        items = list(bar)
        assert len(items) == 5


def test_progressbar_overload_with_show_percent_none():
    """Test the progressbar overload with show_percent=None."""
    with progressbar(
        range(3),
        length=3,
        show_percent=None
    ) as bar:
        assert bar.show_percent is None
        list(bar)  # Consume the iterator


def test_progressbar_overload_with_different_width():
    """Test the progressbar overload with different width values."""
    for width in [20, 50, 100]:
        with progressbar(
            range(2),
            length=2,
            width=width
        ) as bar:
            assert bar.width == width
            list(bar)  # Consume the iterator
