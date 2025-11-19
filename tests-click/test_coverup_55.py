# file: src/click/src/click/utils.py:222-322
# asked: {"lines": [222, 223, 224, 225, 226, 227, 267, 268, 269, 271, 275, 276, 279, 280, 282, 284, 285, 286, 287, 289, 291, 292, 293, 299, 300, 302, 303, 304, 305, 306, 311, 313, 314, 315, 316, 317, 318, 319, 321, 322], "branches": [[267, 268], [267, 279], [268, 269], [268, 271], [275, 276], [275, 279], [279, 280], [279, 282], [284, 285], [284, 291], [286, 287], [286, 289], [291, 292], [291, 299], [299, 300], [299, 311], [302, 303], [302, 321], [313, 314], [313, 315], [315, 316], [315, 321], [316, 317], [316, 318], [318, 319], [318, 321]]}
# gained: {"lines": [222, 223, 224, 225, 226, 227, 267, 268, 269, 271, 275, 276, 279, 280, 282, 284, 285, 286, 287, 289, 291, 292, 293, 299, 300, 302, 303, 304, 305, 306, 311, 313, 314, 315, 321, 322], "branches": [[267, 268], [267, 279], [268, 269], [268, 271], [275, 276], [275, 279], [279, 280], [279, 282], [284, 285], [284, 291], [286, 287], [286, 289], [291, 292], [291, 299], [299, 300], [299, 311], [302, 303], [302, 321], [313, 314], [313, 315], [315, 321]]}

import pytest
import io
import sys
from unittest.mock import Mock, patch, call
from click.utils import echo
from click._compat import WIN

class TestClickUtilsEcho:
    
    def test_echo_with_none_message_and_nl_true(self):
        """Test echo with None message and nl=True (line 291-293)"""
        mock_file = Mock()
        mock_file.flush = Mock()
        
        echo(message=None, file=mock_file, nl=True)
        
        mock_file.flush.assert_called_once()

    def test_echo_with_empty_string_and_nl_true(self):
        """Test echo with empty string and nl=True (line 291-293)"""
        mock_file = Mock()
        mock_file.flush = Mock()
        
        echo(message="", file=mock_file, nl=True)
        
        mock_file.flush.assert_called_once()

    def test_echo_with_bytes_message_and_binary_writer(self):
        """Test echo with bytes message and binary writer (line 299-306)"""
        mock_file = Mock()
        mock_binary_file = Mock()
        mock_file.flush = Mock()
        mock_binary_file.write = Mock()
        mock_binary_file.flush = Mock()
        
        with patch('click.utils._find_binary_writer', return_value=mock_binary_file):
            echo(message=b"test bytes", file=mock_file, nl=False)
            
            mock_file.flush.assert_called_once()
            mock_binary_file.write.assert_called_once_with(b"test bytes")
            mock_binary_file.flush.assert_called_once()

    def test_echo_with_bytearray_message_and_binary_writer(self):
        """Test echo with bytearray message and binary writer (line 299-306)"""
        mock_file = Mock()
        mock_binary_file = Mock()
        mock_file.flush = Mock()
        mock_binary_file.write = Mock()
        mock_binary_file.flush = Mock()
        
        with patch('click.utils._find_binary_writer', return_value=mock_binary_file):
            echo(message=bytearray(b"test bytearray"), file=mock_file, nl=False)
            
            mock_file.flush.assert_called_once()
            mock_binary_file.write.assert_called_once_with(bytearray(b"test bytearray"))
            mock_binary_file.flush.assert_called_once()

    def test_echo_with_bytes_message_no_binary_writer(self):
        """Test echo with bytes message but no binary writer (line 299-306)"""
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.flush = Mock()
        
        with patch('click.utils._find_binary_writer', return_value=None):
            echo(message=b"test bytes", file=mock_file, nl=False)
            
            mock_file.write.assert_called_once_with(b"test bytes")
            mock_file.flush.assert_called_once()

    def test_echo_with_string_and_strip_ansi(self):
        """Test echo with string and strip ANSI (line 313-314)"""
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.flush = Mock()
        
        with patch('click.utils.resolve_color_default', return_value=False), \
             patch('click.utils.should_strip_ansi', return_value=True), \
             patch('click.utils.strip_ansi', return_value="stripped"):
            
            echo(message="\x1b[31mred text\x1b[0m", file=mock_file, nl=False)
            
            mock_file.write.assert_called_once_with("stripped")
            mock_file.flush.assert_called_once()

    def test_echo_with_string_and_win_auto_wrap(self):
        """Test echo with string on Windows with auto_wrap_for_ansi (line 315-317)"""
        if not WIN:
            pytest.skip("Test only relevant on Windows")
            
        mock_file = Mock()
        mock_wrapped_file = Mock()
        mock_wrapped_file.write = Mock()
        mock_wrapped_file.flush = Mock()
        
        with patch('click.utils.resolve_color_default', return_value=True), \
             patch('click.utils.should_strip_ansi', return_value=False), \
             patch('click.utils.auto_wrap_for_ansi', return_value=mock_wrapped_file):
            
            echo(message="test text", file=mock_file, nl=False)
            
            mock_wrapped_file.write.assert_called_once_with("test text")
            mock_wrapped_file.flush.assert_called_once()

    def test_echo_with_string_and_win_no_color_no_auto_wrap(self):
        """Test echo with string on Windows, no color, no auto_wrap (line 318-319)"""
        if not WIN:
            pytest.skip("Test only relevant on Windows")
            
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.flush = Mock()
        
        with patch('click.utils.resolve_color_default', return_value=False), \
             patch('click.utils.should_strip_ansi', return_value=False), \
             patch('click.utils.auto_wrap_for_ansi', return_value=None), \
             patch('click.utils.strip_ansi', return_value="stripped"):
            
            echo(message="\x1b[31mred text\x1b[0m", file=mock_file, nl=False)
            
            mock_file.write.assert_called_once_with("stripped")
            mock_file.flush.assert_called_once()

    def test_echo_with_non_string_bytes_object(self):
        """Test echo with non-string/bytes object (line 279-280)"""
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.flush = Mock()
        
        class CustomObject:
            def __str__(self):
                return "custom object string"
        
        echo(message=CustomObject(), file=mock_file, nl=False)
        
        mock_file.write.assert_called_once_with("custom object string")
        mock_file.flush.assert_called_once()

    def test_echo_with_none_file_and_err_true(self):
        """Test echo with None file and err=True (line 268-269)"""
        mock_stderr = Mock()
        mock_stderr.write = Mock()
        mock_stderr.flush = Mock()
        
        with patch('click.utils._default_text_stderr', return_value=mock_stderr):
            echo(message="test to stderr", file=None, err=True, nl=False)
            
            mock_stderr.write.assert_called_once_with("test to stderr")
            mock_stderr.flush.assert_called_once()

    def test_echo_with_none_file_and_err_false(self):
        """Test echo with None file and err=False (line 271)"""
        mock_stdout = Mock()
        mock_stdout.write = Mock()
        mock_stdout.flush = Mock()
        
        with patch('click.utils._default_text_stdout', return_value=mock_stdout):
            echo(message="test to stdout", file=None, err=False, nl=False)
            
            mock_stdout.write.assert_called_once_with("test to stdout")
            mock_stdout.flush.assert_called_once()

    def test_echo_with_none_file_and_none_streams(self):
        """Test echo with None file and None streams (line 275-276)"""
        with patch('click.utils._default_text_stdout', return_value=None):
            # Should not raise any exception
            echo(message="test", file=None, err=False, nl=False)

    def test_echo_with_string_and_nl_true(self):
        """Test echo with string and nl=True (line 284-287)"""
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.flush = Mock()
        
        echo(message="test", file=mock_file, nl=True)
        
        mock_file.write.assert_called_once_with("test\n")
        mock_file.flush.assert_called_once()

    def test_echo_with_bytes_and_nl_true(self):
        """Test echo with bytes and nl=True (line 284, 288-289)"""
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.flush = Mock()
        
        echo(message=b"test", file=mock_file, nl=True)
        
        # The issue is that when nl=True and message is bytes, the code does:
        # out = out or b''  # which becomes b'test' or b'' -> b'test'
        # then out += b'\n' -> b'test\n'
        # But the mock shows two calls: [call(b''), call(b'test\n')]
        # This suggests the mock is being called with empty bytes first
        # Let's check what actually happens by looking at the call args
        # The issue might be that the mock is being called multiple times
        # Let's use a StringIO to capture the actual output
        output = io.BytesIO()
        echo(message=b"test", file=output, nl=True)
        
        assert output.getvalue() == b"test\n"
        output.close()

    def test_echo_with_none_message_and_nl_false(self):
        """Test echo with None message and nl=False (line 291-293)"""
        mock_file = Mock()
        mock_file.flush = Mock()
        
        echo(message=None, file=mock_file, nl=False)
        
        mock_file.flush.assert_called_once()
