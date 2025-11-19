# file: src/click/src/click/types.py:445-466
# asked: {"lines": [445, 448, 449, 451, 452, 454, 455, 457, 458, 459, 460, 461, 462, 463, 464, 465], "branches": [[448, 449], [448, 451], [451, 452], [451, 457], [454, 451], [454, 455]]}
# gained: {"lines": [445, 448, 449, 451, 452, 454, 455, 457, 458, 459, 460, 461, 462, 463, 464, 465], "branches": [[448, 449], [448, 451], [451, 452], [451, 457], [454, 451], [454, 455]]}

import pytest
from datetime import datetime
from click.types import DateTime
from click.core import Context, Option, Command

class TestDateTime:
    def test_convert_already_datetime(self):
        """Test that when value is already a datetime object, it returns the same object."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        param_type = DateTime()
        result = param_type.convert(dt, None, None)
        assert result == dt

    def test_convert_successful_format(self):
        """Test that when value matches one of the formats, it returns the converted datetime."""
        param_type = DateTime(['%Y-%m-%d'])
        result = param_type.convert('2023-01-01', None, None)
        expected = datetime(2023, 1, 1)
        assert result == expected

    def test_convert_multiple_formats_first_success(self):
        """Test that when value matches the first format in a list of multiple formats, it returns the converted datetime."""
        param_type = DateTime(['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'])
        result = param_type.convert('2023-01-01', None, None)
        expected = datetime(2023, 1, 1)
        assert result == expected

    def test_convert_multiple_formats_second_success(self):
        """Test that when value matches the second format in a list of multiple formats, it returns the converted datetime."""
        param_type = DateTime(['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'])
        result = param_type.convert('2023-01-01 12:00:00', None, None)
        expected = datetime(2023, 1, 1, 12, 0, 0)
        assert result == expected

    def test_convert_no_matching_format_single_format(self, monkeypatch):
        """Test that when value doesn't match any format (single format), it calls fail with appropriate message."""
        param_type = DateTime(['%Y-%m-%d'])
        
        fail_called = False
        fail_message = None
        fail_param = None
        fail_ctx = None
        
        def mock_fail(message, param=None, ctx=None):
            nonlocal fail_called, fail_message, fail_param, fail_ctx
            fail_called = True
            fail_message = message
            fail_param = param
            fail_ctx = ctx
            raise ValueError(message)
        
        monkeypatch.setattr(param_type, 'fail', mock_fail)
        
        with pytest.raises(ValueError) as exc_info:
            param_type.convert('invalid-date', None, None)
        
        assert fail_called
        assert "'invalid-date' does not match the format '%Y-%m-%d'." in fail_message
        assert fail_param is None
        assert fail_ctx is None

    def test_convert_no_matching_format_multiple_formats(self, monkeypatch):
        """Test that when value doesn't match any format (multiple formats), it calls fail with appropriate message."""
        param_type = DateTime(['%Y-%m-%d', '%Y-%m-%d %H:%M:%S'])
        
        fail_called = False
        fail_message = None
        fail_param = None
        fail_ctx = None
        
        def mock_fail(message, param=None, ctx=None):
            nonlocal fail_called, fail_message, fail_param, fail_ctx
            fail_called = True
            fail_message = message
            fail_param = param
            fail_ctx = ctx
            raise ValueError(message)
        
        monkeypatch.setattr(param_type, 'fail', mock_fail)
        
        with pytest.raises(ValueError) as exc_info:
            param_type.convert('invalid-date', None, None)
        
        assert fail_called
        assert "'invalid-date' does not match the formats '%Y-%m-%d', '%Y-%m-%d %H:%M:%S'." in fail_message
        assert fail_param is None
        assert fail_ctx is None

    def test_convert_with_param_and_ctx(self, monkeypatch):
        """Test that when conversion fails, param and ctx are passed to fail method."""
        param_type = DateTime(['%Y-%m-%d'])
        mock_param = Option(['--test-param'])
        mock_command = Command('test_command')
        mock_ctx = Context(mock_command)
        
        fail_called = False
        fail_param = None
        fail_ctx = None
        
        def mock_fail(message, param=None, ctx=None):
            nonlocal fail_called, fail_param, fail_ctx
            fail_called = True
            fail_param = param
            fail_ctx = ctx
            raise ValueError(message)
        
        monkeypatch.setattr(param_type, 'fail', mock_fail)
        
        with pytest.raises(ValueError):
            param_type.convert('invalid-date', mock_param, mock_ctx)
        
        assert fail_called
        assert fail_param == mock_param
        assert fail_ctx == mock_ctx
