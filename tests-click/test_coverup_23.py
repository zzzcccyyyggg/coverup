# file: src/click/src/click/types.py:815-856
# asked: {"lines": [815, 821, 822, 824, 826, 827, 829, 830, 831, 834, 835, 837, 839, 840, 848, 849, 850, 852, 854, 855, 856], "branches": [[821, 822], [821, 824], [829, 830], [829, 839], [834, 835], [834, 837], [848, 849], [848, 854], [849, 850], [849, 852]]}
# gained: {"lines": [815, 821, 822, 824, 826, 827, 829, 830, 831, 834, 835, 837, 839, 840, 848, 849, 850, 852, 854, 855, 856], "branches": [[821, 822], [821, 824], [829, 830], [829, 839], [834, 835], [834, 837], [848, 849], [848, 854], [849, 850], [849, 852]]}

import os
import tempfile
import pytest
from unittest.mock import Mock, patch
from click.types import File
from click.core import Context, Parameter
from click.utils import LazyFile
from click.exceptions import BadParameter
import io

class TestFileTypeCoverage:
    
    def test_convert_with_file_like_object(self):
        """Test that file-like objects are returned directly (line 821-822)"""
        file_obj = io.StringIO("test content")
        file_type = File()
        result = file_type.convert(file_obj, None, None)
        assert result is file_obj
    
    def test_convert_lazy_file_with_context(self):
        """Test lazy file creation with context (lines 829-837)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test")
            tmp_path = tmp.name
        
        try:
            ctx = Mock(spec=Context)
            ctx.call_on_close = Mock()
            
            file_type = File(mode='w', lazy=True)
            result = file_type.convert(tmp_path, None, ctx)
            
            assert isinstance(result, LazyFile)
            ctx.call_on_close.assert_called_once()
            # Verify the callback is for close_intelligently
            callback = ctx.call_on_close.call_args[0][0]
            assert hasattr(callback, '__self__')
            assert callback.__self__ is result
        finally:
            os.unlink(tmp_path)
    
    def test_convert_non_lazy_file_with_context_should_close(self):
        """Test non-lazy file with context that should close (lines 839-850)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test")
            tmp_path = tmp.name
        
        try:
            ctx = Mock(spec=Context)
            ctx.call_on_close = Mock()
            
            file_type = File(mode='r')
            result = file_type.convert(tmp_path, None, ctx)
            
            assert hasattr(result, 'read')
            ctx.call_on_close.assert_called_once()
            # Verify the callback is for close
            callback = ctx.call_on_close.call_args[0][0]
            assert hasattr(callback, '__wrapped__')
            assert callback.__wrapped__.__name__ == 'close'
        finally:
            os.unlink(tmp_path)
    
    def test_convert_non_lazy_file_with_context_no_close(self):
        """Test non-lazy file with context that shouldn't close (lines 839, 848, 852)"""
        ctx = Mock(spec=Context)
        ctx.call_on_close = Mock()
        
        file_type = File(mode='r')
        # Use stdin ('-') which shouldn't be closed
        result = file_type.convert('-', None, ctx)
        
        assert hasattr(result, 'read')
        ctx.call_on_close.assert_called_once()
        # Verify the callback is for flush
        callback = ctx.call_on_close.call_args[0][0]
        assert hasattr(callback, '__wrapped__')
        assert callback.__wrapped__.__name__ == 'flush'
    
    def test_convert_with_os_error(self):
        """Test OSError handling (lines 855-856)"""
        file_type = File()
        param = Mock(spec=Parameter)
        # Create a proper Context mock with the required attributes
        ctx = Mock(spec=Context)
        ctx.command = Mock()
        
        # Try to open a non-existent file
        with pytest.raises(BadParameter) as exc_info:
            file_type.convert('/nonexistent/path/to/file', param, ctx)
        
        # The fail method should be called with appropriate message
        error_message = str(exc_info.value)
        assert "'/nonexistent/path/to/file'" in error_message
        assert param is exc_info.value.param
        assert ctx is exc_info.value.ctx
    
    def test_convert_lazy_file_without_context(self):
        """Test lazy file creation without context (lines 829-837)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test")
            tmp_path = tmp.name
        
        try:
            file_type = File(mode='w', lazy=True)
            result = file_type.convert(tmp_path, None, None)
            
            assert isinstance(result, LazyFile)
            # No context, so no call_on_close should be attempted
        finally:
            os.unlink(tmp_path)
    
    def test_convert_non_lazy_file_without_context(self):
        """Test non-lazy file without context (lines 839-854)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test")
            tmp_path = tmp.name
        
        try:
            file_type = File(mode='r')
            result = file_type.convert(tmp_path, None, None)
            
            assert hasattr(result, 'read')
            # No context, so file should be returned without any cleanup registration
        finally:
            os.unlink(tmp_path)
