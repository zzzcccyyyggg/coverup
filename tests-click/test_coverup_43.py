# file: src/click/src/click/_compat.py:579-604
# asked: {"lines": [579, 583, 585, 586, 588, 589, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 604], "branches": [[588, 589], [588, 591], [595, 596], [595, 597]]}
# gained: {"lines": [579, 583, 585, 586, 588, 589, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 604], "branches": [[588, 589], [588, 591], [595, 596], [595, 597]]}

import pytest
from unittest.mock import Mock, MagicMock
import io
from click._compat import _make_cached_stream_func


class TestMakeCachedStreamFunc:
    def test_src_func_returns_none(self):
        """Test when src_func returns None, the wrapper returns None (lines 588-589)"""
        src_func = Mock(return_value=None)
        wrapper_func = Mock()
        
        cached_func = _make_cached_stream_func(src_func, wrapper_func)
        result = cached_func()
        
        assert result is None
        wrapper_func.assert_not_called()

    def test_cache_get_raises_exception(self):
        """Test when cache.get raises an exception (lines 593-594)"""
        # Create a mock stream that will cause cache.get to fail
        mock_stream = Mock()
        mock_stream.__hash__ = Mock(side_effect=TypeError("unhashable type"))
        
        src_func = Mock(return_value=mock_stream)
        wrapper_func = Mock(return_value=Mock())
        
        cached_func = _make_cached_stream_func(src_func, wrapper_func)
        result = cached_func()
        
        assert result is not None
        wrapper_func.assert_called_once()

    def test_cache_set_raises_exception(self):
        """Test when cache.setitem raises an exception (lines 600-601)"""
        mock_stream = Mock()
        mock_wrapped = Mock()
        
        # Create a WeakKeyDictionary that will raise on setitem
        class FailingWeakKeyDictionary:
            def get(self, key):
                return None
            def __setitem__(self, key, value):
                raise TypeError("Cannot set item")
        
        # Monkeypatch the cache creation
        import click._compat
        with pytest.MonkeyPatch().context() as m:
            m.setattr('click._compat.WeakKeyDictionary', FailingWeakKeyDictionary)
            
            src_func = Mock(return_value=mock_stream)
            wrapper_func = Mock(return_value=mock_wrapped)
            
            cached_func = _make_cached_stream_func(src_func, wrapper_func)
            result = cached_func()
            
            assert result == mock_wrapped
            wrapper_func.assert_called_once()

    def test_cached_value_returned(self):
        """Test when cached value exists and is returned (lines 595-596)"""
        mock_stream = Mock()
        mock_cached = Mock()
        
        # Create a WeakKeyDictionary that returns a cached value
        class MockWeakKeyDictionary:
            def get(self, key):
                return mock_cached
            def __setitem__(self, key, value):
                pass
        
        import click._compat
        with pytest.MonkeyPatch().context() as m:
            m.setattr('click._compat.WeakKeyDictionary', MockWeakKeyDictionary)
            
            src_func = Mock(return_value=mock_stream)
            wrapper_func = Mock()
            
            cached_func = _make_cached_stream_func(src_func, wrapper_func)
            result = cached_func()
            
            assert result is mock_cached
            wrapper_func.assert_not_called()

    def test_normal_flow_with_real_streams(self):
        """Test normal flow with real TextIO streams"""
        src_stream = io.StringIO("test input")
        wrapped_stream = io.StringIO("wrapped output")
        
        src_func = Mock(return_value=src_stream)
        wrapper_func = Mock(return_value=wrapped_stream)
        
        cached_func = _make_cached_stream_func(src_func, wrapper_func)
        
        # First call should call wrapper_func
        result1 = cached_func()
        assert result1 == wrapped_stream
        wrapper_func.assert_called_once()
        
        # Second call should return cached value without calling wrapper_func
        wrapper_func.reset_mock()
        result2 = cached_func()
        assert result2 == wrapped_stream
        wrapper_func.assert_not_called()
