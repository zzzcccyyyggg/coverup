# file: src/flask/src/flask/sansio/scaffold.py:656-698
# asked: {"lines": [656, 657, 669, 670, 671, 672, 673, 674, 677, 679, 681, 682, 683, 688, 689, 690, 695, 696, 698], "branches": [[669, 670], [669, 679], [681, 682], [681, 688], [688, 689], [688, 695], [695, 696], [695, 698]]}
# gained: {"lines": [656, 657, 669, 670, 671, 672, 673, 674, 677, 679, 681, 682, 683, 688, 689, 690, 695, 696, 698], "branches": [[669, 670], [669, 679], [681, 682], [681, 688], [688, 689], [688, 695], [695, 696], [695, 698]]}

import pytest
from werkzeug.exceptions import default_exceptions, HTTPException, NotFound
from flask.sansio.scaffold import Scaffold


class TestScaffoldGetExcClassAndCode:
    """Test cases for Scaffold._get_exc_class_and_code method."""
    
    def test_valid_http_status_code(self):
        """Test with a valid HTTP status code."""
        result = Scaffold._get_exc_class_and_code(404)
        assert result[0] == NotFound
        assert result[1] == 404
    
    def test_invalid_http_status_code(self):
        """Test with an invalid HTTP status code."""
        with pytest.raises(ValueError, match="'999' is not a recognized HTTP error code"):
            Scaffold._get_exc_class_and_code(999)
    
    def test_http_exception_subclass(self):
        """Test with an HTTPException subclass."""
        class CustomHTTPException(HTTPException):
            code = 418
        
        result = Scaffold._get_exc_class_and_code(CustomHTTPException)
        assert result[0] == CustomHTTPException
        assert result[1] == 418
    
    def test_non_http_exception_class(self):
        """Test with a non-HTTP Exception subclass."""
        class CustomException(Exception):
            pass
        
        result = Scaffold._get_exc_class_and_code(CustomException)
        assert result[0] == CustomException
        assert result[1] is None
    
    def test_exception_instance_raises_type_error(self):
        """Test that passing an Exception instance raises TypeError."""
        with pytest.raises(TypeError, match="is an instance, not a class"):
            Scaffold._get_exc_class_and_code(Exception("test"))
    
    def test_non_exception_class_raises_value_error(self):
        """Test that passing a non-Exception class raises ValueError."""
        class NotAnException:
            pass
        
        with pytest.raises(ValueError, match="is not a subclass of Exception"):
            Scaffold._get_exc_class_and_code(NotAnException)
