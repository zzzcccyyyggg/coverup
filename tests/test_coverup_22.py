# file: src/flask/src/flask/sansio/blueprints.py:412-441
# asked: {"lines": [412, 413, 416, 417, 418, 427, 428, 430, 431, 433, 434, 435, 436, 437, 438, 439], "branches": [[427, 428], [427, 430], [430, 431], [430, 433]]}
# gained: {"lines": [412, 413, 416, 417, 418, 427, 428, 430, 431, 433, 434, 435, 436, 437, 438, 439], "branches": [[427, 428], [427, 430], [430, 431], [430, 433]]}

import pytest
from flask.sansio.blueprints import Blueprint

def test_add_url_rule_with_dot_in_endpoint_raises_value_error():
    """Test that add_url_rule raises ValueError when endpoint contains a dot."""
    bp = Blueprint("test", __name__)
    
    with pytest.raises(ValueError, match="'endpoint' may not contain a dot '.' character."):
        bp.add_url_rule("/test", endpoint="test.endpoint")

def test_add_url_rule_with_dot_in_view_func_name_raises_value_error():
    """Test that add_url_rule raises ValueError when view_func name contains a dot."""
    bp = Blueprint("test", __name__)
    
    def view_func_with_dot():
        return "test"
    
    # Set a name with a dot to trigger the error
    view_func_with_dot.__name__ = "view.func"
    
    with pytest.raises(ValueError, match="'view_func' name may not contain a dot '.' character."):
        bp.add_url_rule("/test", view_func=view_func_with_dot)

def test_add_url_rule_successful_registration(mocker):
    """Test that add_url_rule successfully records the rule."""
    bp = Blueprint("test", __name__)
    
    # Mock the record method to verify it's called correctly
    mock_record = mocker.patch.object(bp, 'record')
    
    def view_func():
        return "test"
    
    bp.add_url_rule(
        "/test", 
        endpoint="test_endpoint", 
        view_func=view_func,
        provide_automatic_options=True,
        methods=["GET"]
    )
    
    # Verify record was called with a lambda function
    mock_record.assert_called_once()
    call_arg = mock_record.call_args[0][0]
    assert callable(call_arg)
    
    # Verify the lambda calls add_url_rule with correct parameters
    mock_state = mocker.MagicMock()
    call_arg(mock_state)
    mock_state.add_url_rule.assert_called_once_with(
        "/test",
        "test_endpoint",
        view_func,
        provide_automatic_options=True,
        methods=["GET"]
    )

def test_add_url_rule_without_view_func(mocker):
    """Test that add_url_rule works without a view_func."""
    bp = Blueprint("test", __name__)
    
    mock_record = mocker.patch.object(bp, 'record')
    
    bp.add_url_rule("/test", endpoint="test_endpoint")
    
    mock_record.assert_called_once()
    call_arg = mock_record.call_args[0][0]
    assert callable(call_arg)
    
    mock_state = mocker.MagicMock()
    call_arg(mock_state)
    mock_state.add_url_rule.assert_called_once_with(
        "/test",
        "test_endpoint",
        None,
        provide_automatic_options=None
    )

def test_add_url_rule_with_provide_automatic_options(mocker):
    """Test that add_url_rule passes provide_automatic_options correctly."""
    bp = Blueprint("test", __name__)
    
    mock_record = mocker.patch.object(bp, 'record')
    
    def view_func():
        return "test"
    
    bp.add_url_rule(
        "/test", 
        view_func=view_func,
        provide_automatic_options=False
    )
    
    mock_record.assert_called_once()
    call_arg = mock_record.call_args[0][0]
    assert callable(call_arg)
    
    mock_state = mocker.MagicMock()
    call_arg(mock_state)
    mock_state.add_url_rule.assert_called_once_with(
        "/test",
        None,
        view_func,
        provide_automatic_options=False
    )
