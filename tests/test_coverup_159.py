# file: src/flask/src/flask/sansio/app.py:533-544
# asked: {"lines": [533, 542, 543, 544], "branches": [[542, 543], [542, 544]]}
# gained: {"lines": [533, 542, 543, 544], "branches": [[542, 543], [542, 544]]}

import pytest
from flask import Flask


class TestSelectJinjaAutoescape:
    """Test cases for App.select_jinja_autoescape method."""
    
    def test_select_jinja_autoescape_none_filename(self):
        """Test that None filename returns True."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape(None)
        assert result is True
    
    def test_select_jinja_autoescape_html_extension(self):
        """Test that .html extension returns True."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape("template.html")
        assert result is True
    
    def test_select_jinja_autoescape_htm_extension(self):
        """Test that .htm extension returns True."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape("template.htm")
        assert result is True
    
    def test_select_jinja_autoescape_xml_extension(self):
        """Test that .xml extension returns True."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape("template.xml")
        assert result is True
    
    def test_select_jinja_autoescape_xhtml_extension(self):
        """Test that .xhtml extension returns True."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape("template.xhtml")
        assert result is True
    
    def test_select_jinja_autoescape_svg_extension(self):
        """Test that .svg extension returns True."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape("template.svg")
        assert result is True
    
    def test_select_jinja_autoescape_other_extension(self):
        """Test that non-autoescaped extension returns False."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape("template.txt")
        assert result is False
    
    def test_select_jinja_autoescape_no_extension(self):
        """Test that filename without extension returns False."""
        app = Flask(__name__)
        result = app.select_jinja_autoescape("template")
        assert result is False
