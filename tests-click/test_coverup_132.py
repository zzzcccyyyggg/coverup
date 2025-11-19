# file: src/click/src/click/core.py:1255-1269
# asked: {"lines": [1255, 1259, 1260, 1261, 1263, 1264, 1265, 1266, 1268, 1269], "branches": [[1259, 1260], [1259, 1268], [1268, 0], [1268, 1269]]}
# gained: {"lines": [1255, 1259, 1260, 1261, 1263, 1264, 1265, 1266, 1268, 1269], "branches": [[1259, 1260], [1259, 1268], [1268, 0], [1268, 1269]]}

import pytest
from click.core import Command, Context
from unittest.mock import Mock, patch

class TestCommandInvoke:
    def test_invoke_with_deprecated_true_and_callback(self, monkeypatch):
        """Test that invoke prints deprecation warning when deprecated=True and has callback"""
        mock_echo = Mock()
        monkeypatch.setattr('click.core.echo', mock_echo)
        
        callback = Mock(return_value="callback_result")
        cmd = Command(name="test_cmd", deprecated=True, callback=callback)
        ctx = Context(cmd)
        ctx.params = {"param1": "value1"}
        
        result = cmd.invoke(ctx)
        
        # Verify deprecation warning was printed
        assert mock_echo.called
        call_args = mock_echo.call_args[0]
        message = call_args[0]
        assert "DeprecationWarning" in message
        assert "test_cmd" in message
        assert "is deprecated" in message
        # Check that err=True was passed as keyword argument
        assert mock_echo.call_args[1] == {"err": True}
        
        # Verify callback was invoked with correct parameters
        callback.assert_called_once_with(param1="value1")
        assert result == "callback_result"

    def test_invoke_with_deprecated_string_and_callback(self, monkeypatch):
        """Test that invoke prints custom deprecation message when deprecated is a string and has callback"""
        mock_echo = Mock()
        monkeypatch.setattr('click.core.echo', mock_echo)
        
        callback = Mock(return_value="callback_result")
        cmd = Command(name="test_cmd", deprecated="Use new_cmd instead", callback=callback)
        ctx = Context(cmd)
        ctx.params = {"param1": "value1"}
        
        result = cmd.invoke(ctx)
        
        # Verify custom deprecation warning was printed
        assert mock_echo.called
        call_args = mock_echo.call_args[0]
        message = call_args[0]
        assert "DeprecationWarning" in message
        assert "test_cmd" in message
        assert "is deprecated" in message
        assert "Use new_cmd instead" in message
        # Check that err=True was passed as keyword argument
        assert mock_echo.call_args[1] == {"err": True}
        
        # Verify callback was invoked with correct parameters
        callback.assert_called_once_with(param1="value1")
        assert result == "callback_result"

    def test_invoke_with_deprecated_true_and_no_callback(self, monkeypatch):
        """Test that invoke prints deprecation warning when deprecated=True but no callback"""
        mock_echo = Mock()
        monkeypatch.setattr('click.core.echo', mock_echo)
        
        cmd = Command(name="test_cmd", deprecated=True, callback=None)
        ctx = Context(cmd)
        ctx.params = {}
        
        result = cmd.invoke(ctx)
        
        # Verify deprecation warning was printed
        assert mock_echo.called
        call_args = mock_echo.call_args[0]
        message = call_args[0]
        assert "DeprecationWarning" in message
        assert "test_cmd" in message
        assert "is deprecated" in message
        # Check that err=True was passed as keyword argument
        assert mock_echo.call_args[1] == {"err": True}
        
        # Verify no callback was invoked and result is None
        assert result is None

    def test_invoke_with_deprecated_false_and_callback(self):
        """Test that invoke does not print deprecation warning when deprecated=False and has callback"""
        callback = Mock(return_value="callback_result")
        cmd = Command(name="test_cmd", deprecated=False, callback=callback)
        ctx = Context(cmd)
        ctx.params = {"param1": "value1"}
        
        with patch('click.core.echo') as mock_echo:
            result = cmd.invoke(ctx)
            
            # Verify no deprecation warning was printed
            mock_echo.assert_not_called()
            
            # Verify callback was invoked with correct parameters
            callback.assert_called_once_with(param1="value1")
            assert result == "callback_result"

    def test_invoke_with_deprecated_false_and_no_callback(self):
        """Test that invoke does nothing when deprecated=False and no callback"""
        cmd = Command(name="test_cmd", deprecated=False, callback=None)
        ctx = Context(cmd)
        ctx.params = {}
        
        with patch('click.core.echo') as mock_echo:
            result = cmd.invoke(ctx)
            
            # Verify no deprecation warning was printed
            mock_echo.assert_not_called()
            
            # Verify no callback was invoked and result is None
            assert result is None
