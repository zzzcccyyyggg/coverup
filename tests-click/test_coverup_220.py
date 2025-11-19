# file: src/click/src/click/_compat.py:492-496
# asked: {"lines": [492, 493, 494, 496], "branches": [[493, 494], [493, 496]]}
# gained: {"lines": [492, 493, 494, 496], "branches": [[493, 494], [493, 496]]}

import pytest
import typing as t
from unittest.mock import Mock, MagicMock
from click._compat import _is_jupyter_kernel_output, _FixupStream, _NonClosingTextIOWrapper


class TestIsJupyterKernelOutput:
    
    def test_direct_ipykernel_stream(self, monkeypatch):
        """Test when stream is directly an ipykernel stream"""
        mock_stream = Mock()
        mock_stream.__class__.__module__ = "ipykernel.some_module"
        
        result = _is_jupyter_kernel_output(mock_stream)
        
        assert result is True

    def test_non_ipykernel_stream(self, monkeypatch):
        """Test when stream is not an ipykernel stream"""
        mock_stream = Mock()
        mock_stream.__class__.__module__ = "some_other_module"
        
        result = _is_jupyter_kernel_output(mock_stream)
        
        assert result is False

    def test_fixup_stream_wrapping_ipykernel(self, monkeypatch):
        """Test when stream is wrapped in _FixupStream but underlying is ipykernel"""
        mock_inner_stream = Mock()
        mock_inner_stream.__class__.__module__ = "ipykernel.inner_module"
        
        fixup_stream = _FixupStream(mock_inner_stream)
        
        result = _is_jupyter_kernel_output(fixup_stream)
        
        assert result is True

    def test_nonclosing_textio_wrapper_wrapping_ipykernel(self, monkeypatch):
        """Test when stream is wrapped in _NonClosingTextIOWrapper but underlying is ipykernel"""
        mock_inner_stream = Mock()
        mock_inner_stream.__class__.__module__ = "ipykernel.inner_module"
        
        nonclosing_wrapper = _NonClosingTextIOWrapper(mock_inner_stream, encoding='utf-8', errors='strict')
        
        result = _is_jupyter_kernel_output(nonclosing_wrapper)
        
        assert result is True

    def test_multiple_wrappers_ipykernel(self, monkeypatch):
        """Test when stream is wrapped multiple times but underlying is ipykernel"""
        mock_inner_stream = Mock()
        mock_inner_stream.__class__.__module__ = "ipykernel.deep_module"
        
        fixup_stream = _FixupStream(mock_inner_stream)
        nonclosing_wrapper = _NonClosingTextIOWrapper(fixup_stream, encoding='utf-8', errors='strict')
        another_fixup = _FixupStream(nonclosing_wrapper)
        
        result = _is_jupyter_kernel_output(another_fixup)
        
        assert result is True

    def test_multiple_wrappers_non_ipykernel(self, monkeypatch):
        """Test when stream is wrapped multiple times but underlying is not ipykernel"""
        mock_inner_stream = Mock()
        mock_inner_stream.__class__.__module__ = "regular_module"
        
        fixup_stream = _FixupStream(mock_inner_stream)
        nonclosing_wrapper = _NonClosingTextIOWrapper(fixup_stream, encoding='utf-8', errors='strict')
        another_fixup = _FixupStream(nonclosing_wrapper)
        
        result = _is_jupyter_kernel_output(another_fixup)
        
        assert result is False
