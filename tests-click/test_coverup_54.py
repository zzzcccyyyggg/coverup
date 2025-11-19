# file: src/click/src/click/_termui_impl.py:369-408
# asked: {"lines": [369, 371, 375, 376, 378, 379, 382, 383, 384, 385, 386, 387, 388, 390, 391, 392, 393, 395, 396, 397, 399, 401, 402, 403, 404, 405, 406, 408], "branches": [[375, 376], [375, 378], [378, 379], [378, 382], [383, 384], [383, 390], [384, 385], [384, 387], [385, 386], [385, 390], [387, 388], [387, 390], [390, 391], [390, 392], [392, 395], [392, 396], [396, 397], [396, 399], [404, 405], [404, 406]]}
# gained: {"lines": [369, 371, 375, 376, 378, 379, 382, 383, 384, 385, 386, 387, 388, 390, 391, 392, 393, 395, 396, 397, 399, 401, 402, 403, 404, 405, 406, 408], "branches": [[375, 376], [375, 378], [378, 379], [378, 382], [383, 384], [383, 390], [384, 385], [384, 387], [385, 386], [385, 390], [387, 388], [387, 390], [390, 391], [390, 392], [392, 395], [392, 396], [396, 397], [396, 399], [404, 405], [404, 406]]}

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import tempfile
from click._termui_impl import pager, _nullpager, _pipepager, _tempfilepager


class TestPagerCoverage:
    def test_pager_stdout_none(self, monkeypatch):
        """Test pager when stdout is None (lines 375-376)"""
        monkeypatch.setattr('click._termui_impl._default_text_stdout', lambda: None)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._nullpager') as mock_nullpager:
            pager(generator)
            mock_nullpager.assert_called_once()
            args = mock_nullpager.call_args[0]
            assert isinstance(args[0], StringIO)
            assert args[1] == generator
            assert args[2] is None

    def test_pager_not_tty(self, monkeypatch):
        """Test pager when stdin or stdout is not a TTY (lines 378-379)"""
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._nullpager') as mock_nullpager:
            pager(generator)
            mock_nullpager.assert_called_once()

    def test_pager_env_pager_win_tempfile_success(self, monkeypatch):
        """Test pager with PAGER env var on Windows using tempfile (lines 382-386)"""
        monkeypatch.setattr('click._termui_impl.WIN', True)
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.setenv('PAGER', 'testpager')
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._tempfilepager') as mock_tempfilepager:
            mock_tempfilepager.return_value = True
            pager(generator)
            mock_tempfilepager.assert_called_once_with(generator, ['testpager'], None)

    def test_pager_env_pager_win_tempfile_fail(self, monkeypatch):
        """Test pager with PAGER env var on Windows when tempfile fails (lines 382-387)"""
        monkeypatch.setattr('click._termui_impl.WIN', True)
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.setenv('PAGER', 'testpager')
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._tempfilepager') as mock_tempfilepager:
            mock_tempfilepager.return_value = False
            with patch('click._termui_impl._pipepager') as mock_pipepager:
                mock_pipepager.return_value = False
                pager(generator)
                # The pager will try multiple methods, so we check that our specific call was made
                mock_tempfilepager.assert_any_call(generator, ['testpager'], None)

    def test_pager_env_pager_non_win_pipe_success(self, monkeypatch):
        """Test pager with PAGER env var on non-Windows using pipe (lines 382-387)"""
        monkeypatch.setattr('click._termui_impl.WIN', False)
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.setenv('PAGER', 'testpager')
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._pipepager') as mock_pipepager:
            mock_pipepager.return_value = True
            pager(generator)
            mock_pipepager.assert_called_once_with(generator, ['testpager'], None)

    def test_pager_env_pager_non_win_pipe_fail(self, monkeypatch):
        """Test pager with PAGER env var on non-Windows when pipe fails (lines 382-388)"""
        monkeypatch.setattr('click._termui_impl.WIN', False)
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.setenv('PAGER', 'testpager')
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._pipepager') as mock_pipepager:
            mock_pipepager.return_value = False
            pager(generator)
            # The pager will try multiple methods, so we check that our specific call was made
            mock_pipepager.assert_any_call(generator, ['testpager'], None)

    def test_pager_dumb_term(self, monkeypatch):
        """Test pager with TERM=dumb (lines 390-391)"""
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.setenv('TERM', 'dumb')
        monkeypatch.delenv('PAGER', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._nullpager') as mock_nullpager:
            pager(generator)
            mock_nullpager.assert_called_once()

    def test_pager_emacs_term(self, monkeypatch):
        """Test pager with TERM=emacs (lines 390-391)"""
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.setenv('TERM', 'emacs')
        monkeypatch.delenv('PAGER', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._nullpager') as mock_nullpager:
            pager(generator)
            mock_nullpager.assert_called_once()

    def test_pager_win_more_success(self, monkeypatch):
        """Test pager on Windows with 'more' command success (lines 392-395)"""
        monkeypatch.setattr('click._termui_impl.WIN', True)
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.delenv('PAGER', raising=False)
        monkeypatch.delenv('TERM', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._tempfilepager') as mock_tempfilepager:
            mock_tempfilepager.return_value = True
            pager(generator)
            mock_tempfilepager.assert_called_once_with(generator, ['more'], None)

    def test_pager_os2_more_success(self, monkeypatch):
        """Test pager on OS/2 with 'more' command success (lines 392-395)"""
        monkeypatch.setattr('click._termui_impl.WIN', False)
        monkeypatch.setattr('sys.platform', 'os2')
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.delenv('PAGER', raising=False)
        monkeypatch.delenv('TERM', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._tempfilepager') as mock_tempfilepager:
            mock_tempfilepager.return_value = True
            pager(generator)
            mock_tempfilepager.assert_called_once_with(generator, ['more'], None)

    def test_pager_win_more_fail(self, monkeypatch):
        """Test pager on Windows when 'more' fails (lines 392-395)"""
        monkeypatch.setattr('click._termui_impl.WIN', True)
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.delenv('PAGER', raising=False)
        monkeypatch.delenv('TERM', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._tempfilepager') as mock_tempfilepager:
            mock_tempfilepager.return_value = False
            with patch('click._termui_impl._pipepager') as mock_pipepager:
                mock_pipepager.return_value = False
                pager(generator)
                mock_tempfilepager.assert_any_call(generator, ['more'], None)

    def test_pager_less_success(self, monkeypatch):
        """Test pager with 'less' command success (lines 396-397)"""
        monkeypatch.setattr('click._termui_impl.WIN', False)
        monkeypatch.setattr('sys.platform', 'linux')
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.delenv('PAGER', raising=False)
        monkeypatch.delenv('TERM', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._pipepager') as mock_pipepager:
            mock_pipepager.return_value = True
            pager(generator)
            mock_pipepager.assert_called_once_with(generator, ['less'], None)

    def test_pager_less_fail(self, monkeypatch):
        """Test pager when 'less' fails (lines 396-397)"""
        monkeypatch.setattr('click._termui_impl.WIN', False)
        monkeypatch.setattr('sys.platform', 'linux')
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.delenv('PAGER', raising=False)
        monkeypatch.delenv('TERM', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._pipepager') as mock_pipepager:
            mock_pipepager.return_value = False
            with patch('tempfile.mkstemp') as mock_mkstemp:
                mock_mkstemp.return_value = (123, '/tmp/testfile')
                with patch('os.close') as mock_close:
                    with patch('click._termui_impl._nullpager') as mock_nullpager:
                        with patch('os.unlink') as mock_unlink:
                            pager(generator)
                            # The pager will try multiple methods, so we check that our specific calls were made
                            mock_pipepager.assert_any_call(generator, ['less'], None)
                            mock_pipepager.assert_any_call(generator, ['more'], None)
                            mock_nullpager.assert_called_once()
                            mock_unlink.assert_called_once_with('/tmp/testfile')

    def test_pager_fallback_more_success(self, monkeypatch):
        """Test pager fallback with 'more' via pipe success (lines 399-405)"""
        monkeypatch.setattr('click._termui_impl.WIN', False)
        monkeypatch.setattr('sys.platform', 'linux')
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.delenv('PAGER', raising=False)
        monkeypatch.delenv('TERM', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._pipepager') as mock_pipepager:
            mock_pipepager.side_effect = [False, True]  # less fails, more succeeds
            with patch('tempfile.mkstemp') as mock_mkstemp:
                mock_mkstemp.return_value = (123, '/tmp/testfile')
                with patch('os.close') as mock_close:
                    with patch('os.unlink') as mock_unlink:
                        pager(generator)
                        assert mock_pipepager.call_count == 2
                        mock_pipepager.assert_any_call(generator, ['less'], None)
                        mock_pipepager.assert_any_call(generator, ['more'], None)
                        mock_unlink.assert_called_once_with('/tmp/testfile')

    def test_pager_fallback_nullpager(self, monkeypatch):
        """Test pager ultimate fallback to nullpager (lines 399-406)"""
        monkeypatch.setattr('click._termui_impl.WIN', False)
        monkeypatch.setattr('sys.platform', 'linux')
        monkeypatch.setattr('click._termui_impl.isatty', lambda x: True)
        monkeypatch.delenv('PAGER', raising=False)
        monkeypatch.delenv('TERM', raising=False)
        generator = ["line1\n", "line2\n"]
        
        with patch('click._termui_impl._pipepager') as mock_pipepager:
            mock_pipepager.return_value = False  # both less and more fail
            with patch('tempfile.mkstemp') as mock_mkstemp:
                mock_mkstemp.return_value = (123, '/tmp/testfile')
                with patch('os.close') as mock_close:
                    with patch('click._termui_impl._nullpager') as mock_nullpager:
                        with patch('os.unlink') as mock_unlink:
                            pager(generator)
                            assert mock_pipepager.call_count == 2
                            mock_pipepager.assert_any_call(generator, ['less'], None)
                            mock_pipepager.assert_any_call(generator, ['more'], None)
                            mock_nullpager.assert_called_once()
                            mock_unlink.assert_called_once_with('/tmp/testfile')
