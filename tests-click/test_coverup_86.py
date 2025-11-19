# file: src/click/src/click/utils.py:498-520
# asked: {"lines": [498, 499, 507, 508, 510, 511, 512, 513, 514, 516, 517, 519, 520], "branches": [[516, 0], [516, 517]]}
# gained: {"lines": [498, 499, 507, 508, 510, 511, 512, 513, 514, 516, 517, 519, 520], "branches": [[516, 0], [516, 517]]}

import pytest
import errno
from unittest.mock import Mock
from click.utils import PacifyFlushWrapper

class TestPacifyFlushWrapper:
    def test_flush_suppresses_broken_pipe_error(self):
        """Test that flush suppresses EPIPE (BrokenPipeError) but re-raises other OSErrors"""
        mock_wrapped = Mock()
        mock_wrapped.flush.side_effect = OSError(errno.EPIPE, "Broken pipe")
        
        wrapper = PacifyFlushWrapper(mock_wrapped)
        
        # This should not raise an exception
        wrapper.flush()
        
        mock_wrapped.flush.assert_called_once()

    def test_flush_reraises_other_oserrors(self):
        """Test that flush re-raises OSErrors that are not EPIPE"""
        mock_wrapped = Mock()
        mock_wrapped.flush.side_effect = OSError(errno.EACCES, "Permission denied")
        
        wrapper = PacifyFlushWrapper(mock_wrapped)
        
        with pytest.raises(OSError) as exc_info:
            wrapper.flush()
        
        assert exc_info.value.errno == errno.EACCES
        mock_wrapped.flush.assert_called_once()

    def test_flush_normal_operation(self):
        """Test that flush works normally when no exception occurs"""
        mock_wrapped = Mock()
        
        wrapper = PacifyFlushWrapper(mock_wrapped)
        wrapper.flush()
        
        mock_wrapped.flush.assert_called_once()

    def test_getattr_proxies_attributes(self):
        """Test that __getattr__ proxies attributes to the wrapped object"""
        mock_wrapped = Mock()
        mock_wrapped.name = "test_stream"
        mock_wrapped.mode = "w"
        
        wrapper = PacifyFlushWrapper(mock_wrapped)
        
        assert wrapper.name == "test_stream"
        assert wrapper.mode == "w"

    def test_getattr_proxies_methods(self):
        """Test that __getattr__ proxies methods to the wrapped object"""
        mock_wrapped = Mock()
        mock_wrapped.write.return_value = 5
        
        wrapper = PacifyFlushWrapper(mock_wrapped)
        
        result = wrapper.write("hello")
        
        assert result == 5
        mock_wrapped.write.assert_called_once_with("hello")

    def test_init_sets_wrapped_attribute(self):
        """Test that __init__ correctly sets the wrapped attribute"""
        mock_wrapped = Mock()
        
        wrapper = PacifyFlushWrapper(mock_wrapped)
        
        assert wrapper.wrapped is mock_wrapped
