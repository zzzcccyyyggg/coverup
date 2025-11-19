# file: src/click/src/click/shell_completion.py:310-341
# asked: {"lines": [310, 311, 312, 313, 315, 317, 318, 320, 321, 322, 324, 326, 327, 329, 330, 331, 332, 335, 338, 339, 340], "branches": [[317, 318], [317, 320], [326, 327], [326, 338], [329, 0], [329, 330]]}
# gained: {"lines": [310, 311, 312, 313, 315, 317, 318, 320, 321, 322, 324, 326, 327, 329, 330, 331, 332, 335, 338, 339, 340], "branches": [[317, 318], [317, 320], [326, 327], [326, 338], [329, 0], [329, 330]]}

import pytest
import re
from unittest.mock import patch, MagicMock
from click.shell_completion import BashComplete


class TestBashComplete:
    """Test cases for BashComplete._check_version method."""

    def test_check_version_bash_not_found(self, monkeypatch):
        """Test when bash executable is not found."""
        monkeypatch.setattr("shutil.which", lambda x: None)
        
        with patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_called_once_with(
            "Couldn't detect Bash version, shell completion is not supported.",
            err=True
        )

    def test_check_version_bash_old_version_4_3(self, monkeypatch):
        """Test when bash version is 4.3 (too old)."""
        monkeypatch.setattr("shutil.which", lambda x: "/bin/bash")
        
        mock_run = MagicMock()
        mock_run.stdout = b"4.3.0\n"
        
        with patch("subprocess.run", return_value=mock_run), \
             patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_called_once_with(
            "Shell completion is not supported for Bash versions older than 4.4.",
            err=True
        )

    def test_check_version_bash_old_version_3_9(self, monkeypatch):
        """Test when bash version is 3.9 (too old)."""
        monkeypatch.setattr("shutil.which", lambda x: "/bin/bash")
        
        mock_run = MagicMock()
        mock_run.stdout = b"3.9.0\n"
        
        with patch("subprocess.run", return_value=mock_run), \
             patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_called_once_with(
            "Shell completion is not supported for Bash versions older than 4.4.",
            err=True
        )

    def test_check_version_bash_version_4_4(self, monkeypatch):
        """Test when bash version is 4.4 (supported)."""
        monkeypatch.setattr("shutil.which", lambda x: "/bin/bash")
        
        mock_run = MagicMock()
        mock_run.stdout = b"4.4.0\n"
        
        with patch("subprocess.run", return_value=mock_run), \
             patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_not_called()

    def test_check_version_bash_version_5_0(self, monkeypatch):
        """Test when bash version is 5.0 (supported)."""
        monkeypatch.setattr("shutil.which", lambda x: "/bin/bash")
        
        mock_run = MagicMock()
        mock_run.stdout = b"5.0.0\n"
        
        with patch("subprocess.run", return_value=mock_run), \
             patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_not_called()

    def test_check_version_bash_version_4_4_with_patch(self, monkeypatch):
        """Test when bash version is 4.4.19 (supported)."""
        monkeypatch.setattr("shutil.which", lambda x: "/bin/bash")
        
        mock_run = MagicMock()
        mock_run.stdout = b"4.4.19\n"
        
        with patch("subprocess.run", return_value=mock_run), \
             patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_not_called()

    def test_check_version_bash_version_invalid_format(self, monkeypatch):
        """Test when bash version output has invalid format."""
        monkeypatch.setattr("shutil.which", lambda x: "/bin/bash")
        
        mock_run = MagicMock()
        mock_run.stdout = b"invalid-version-string\n"
        
        with patch("subprocess.run", return_value=mock_run), \
             patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_called_once_with(
            "Couldn't detect Bash version, shell completion is not supported.",
            err=True
        )

    def test_check_version_bash_version_empty_output(self, monkeypatch):
        """Test when bash version output is empty."""
        monkeypatch.setattr("shutil.which", lambda x: "/bin/bash")
        
        mock_run = MagicMock()
        mock_run.stdout = b"\n"
        
        with patch("subprocess.run", return_value=mock_run), \
             patch("click.shell_completion.echo") as mock_echo:
            BashComplete._check_version()
            
        mock_echo.assert_called_once_with(
            "Couldn't detect Bash version, shell completion is not supported.",
            err=True
        )
