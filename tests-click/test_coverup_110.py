# file: src/click/src/click/termui.py:507-515
# asked: {"lines": [507, 508, 509, 511, 512, 513, 515], "branches": [[508, 509], [508, 511], [511, 512], [511, 515]]}
# gained: {"lines": [507, 508, 509, 511, 512, 513, 515], "branches": [[508, 509], [508, 511], [511, 512], [511, 515]]}

import pytest
from click.termui import _interpret_color

class TestInterpretColor:
    def test_interpret_color_with_int(self):
        """Test _interpret_color with integer color and offset."""
        result = _interpret_color(42, offset=5)
        assert result == "43;5;42"
    
    def test_interpret_color_with_tuple(self):
        """Test _interpret_color with tuple color and offset."""
        result = _interpret_color((100, 150, 200), offset=2)
        assert result == "40;2;100;150;200"
    
    def test_interpret_color_with_list(self):
        """Test _interpret_color with list color and offset."""
        result = _interpret_color([50, 75, 100], offset=1)
        assert result == "39;2;50;75;100"
    
    def test_interpret_color_with_named_color(self):
        """Test _interpret_color with named color and offset."""
        result = _interpret_color("red", offset=3)
        assert result == "34"
    
    def test_interpret_color_with_named_color_no_offset(self):
        """Test _interpret_color with named color and no offset."""
        result = _interpret_color("green")
        assert result == "32"
    
    def test_interpret_color_with_int_no_offset(self):
        """Test _interpret_color with integer color and no offset."""
        result = _interpret_color(15)
        assert result == "38;5;15"
    
    def test_interpret_color_with_tuple_no_offset(self):
        """Test _interpret_color with tuple color and no offset."""
        result = _interpret_color((10, 20, 30))
        assert result == "38;2;10;20;30"
