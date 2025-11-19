# file: src/flask/src/flask/sansio/app.py:601-658
# asked: {"lines": [601, 602, 605, 606, 607, 610, 611, 612, 613, 618, 619, 620, 621, 622, 625, 628, 632, 633, 634, 637, 638, 639, 640, 642, 645, 647, 648, 650, 651, 652, 653, 654, 655, 656, 658], "branches": [[610, 611], [610, 612], [618, 619], [618, 620], [620, 621], [620, 625], [632, 633], [632, 637], [637, 638], [637, 645], [638, 639], [638, 642], [651, 0], [651, 652], [653, 654], [653, 658]]}
# gained: {"lines": [601, 602, 605, 606, 607, 610, 611, 612, 613, 618, 619, 620, 621, 622, 625, 628, 632, 633, 634, 637, 638, 639, 640, 642, 645, 647, 648, 650, 651, 652, 653, 654, 655, 656, 658], "branches": [[610, 611], [610, 612], [618, 619], [618, 620], [620, 621], [620, 625], [632, 633], [637, 638], [637, 645], [638, 639], [638, 642], [651, 0], [651, 652], [653, 654], [653, 658]]}

import pytest
from flask import Flask
from flask.sansio.scaffold import _endpoint_from_view_func

def test_add_url_rule_with_string_methods():
    """Test that passing a string for methods raises TypeError."""
    app = Flask(__name__)
    
    def view_func():
        return "test"
    
    with pytest.raises(TypeError, match="Allowed methods must be a list of strings"):
        app.add_url_rule("/test", view_func=view_func, methods="POST")

def test_add_url_rule_provide_automatic_options_none_with_OPTIONS_not_in_methods():
    """Test automatic OPTIONS handling when OPTIONS not in methods and PROVIDE_AUTOMATIC_OPTIONS is True."""
    app = Flask(__name__)
    app.config["PROVIDE_AUTOMATIC_OPTIONS"] = True
    
    def view_func():
        return "test"
    
    # This should trigger the path where provide_automatic_options becomes True
    # and OPTIONS gets added to required_methods
    app.add_url_rule("/test", view_func=view_func, methods=["GET", "POST"])
    
    # Find our custom rule, not the static rule
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    assert rule.provide_automatic_options is True
    assert "OPTIONS" in rule.methods

def test_add_url_rule_provide_automatic_options_none_with_OPTIONS_in_methods():
    """Test automatic OPTIONS handling when OPTIONS is already in methods."""
    app = Flask(__name__)
    app.config["PROVIDE_AUTOMATIC_OPTIONS"] = True
    
    def view_func():
        return "test"
    
    # OPTIONS is already in methods, so provide_automatic_options should become False
    app.add_url_rule("/test", view_func=view_func, methods=["GET", "POST", "OPTIONS"])
    
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    assert rule.provide_automatic_options is False
    assert "OPTIONS" in rule.methods

def test_add_url_rule_provide_automatic_options_none_with_PROVIDE_AUTOMATIC_OPTIONS_false():
    """Test automatic OPTIONS handling when PROVIDE_AUTOMATIC_OPTIONS is False."""
    app = Flask(__name__)
    app.config["PROVIDE_AUTOMATIC_OPTIONS"] = False
    
    def view_func():
        return "test"
    
    # With PROVIDE_AUTOMATIC_OPTIONS=False, provide_automatic_options should become False
    app.add_url_rule("/test", view_func=view_func, methods=["GET", "POST"])
    
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    assert rule.provide_automatic_options is False
    assert "OPTIONS" not in rule.methods

def test_add_url_rule_with_required_methods():
    """Test that required_methods from view_func are added to methods."""
    app = Flask(__name__)
    
    def view_func():
        return "test"
    
    # Add required_methods attribute to the view function
    view_func.required_methods = {"HEAD", "PUT"}
    
    app.add_url_rule("/test", view_func=view_func, methods=["GET", "POST"])
    
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    assert "GET" in rule.methods
    assert "POST" in rule.methods
    assert "HEAD" in rule.methods
    assert "PUT" in rule.methods

def test_add_url_rule_overwriting_existing_endpoint():
    """Test that overwriting an existing endpoint raises AssertionError."""
    app = Flask(__name__)
    
    def view_func1():
        return "test1"
    
    def view_func2():
        return "test2"
    
    # Add first view function
    app.add_url_rule("/test1", view_func=view_func1, endpoint="same_endpoint")
    
    # Try to add second view function with same endpoint - should raise AssertionError
    with pytest.raises(AssertionError, match="View function mapping is overwriting an existing endpoint function"):
        app.add_url_rule("/test2", view_func=view_func2, endpoint="same_endpoint")

def test_add_url_rule_with_view_func_provide_automatic_options():
    """Test provide_automatic_options from view_func attribute."""
    app = Flask(__name__)
    
    def view_func():
        return "test"
    
    # Set provide_automatic_options on the view function
    view_func.provide_automatic_options = False
    
    app.add_url_rule("/test", view_func=view_func, methods=["GET"])
    
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    assert rule.provide_automatic_options is False

def test_add_url_rule_without_view_func():
    """Test add_url_rule without view_func (for blueprint registration)."""
    app = Flask(__name__)
    
    # Should not raise any errors
    app.add_url_rule("/test", endpoint="test_endpoint")
    
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    assert rule.endpoint == "test_endpoint"
    assert "GET" in rule.methods

def test_add_url_rule_with_methods_from_view_func():
    """Test that methods are taken from view_func.methods when not provided."""
    app = Flask(__name__)
    
    def view_func():
        return "test"
    
    view_func.methods = ["POST", "PUT"]
    
    app.add_url_rule("/test", view_func=view_func)
    
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    assert "POST" in rule.methods
    assert "PUT" in rule.methods
    assert "GET" not in rule.methods

def test_add_url_rule_default_methods():
    """Test default methods when neither methods parameter nor view_func.methods exist."""
    app = Flask(__name__)
    
    def view_func():
        return "test"
    
    app.add_url_rule("/test", view_func=view_func)
    
    rules = [rule for rule in app.url_map.iter_rules() if rule.rule == "/test"]
    assert len(rules) == 1
    rule = rules[0]
    # Flask automatically adds HEAD and OPTIONS to GET methods
    assert "GET" in rule.methods
    assert "HEAD" in rule.methods
    assert "OPTIONS" in rule.methods
