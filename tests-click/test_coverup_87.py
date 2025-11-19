# file: src/click/src/click/exceptions.py:277-291
# asked: {"lines": [277, 278, 280, 281, 282, 284, 285, 286, 288, 289, 290], "branches": [[281, 282], [281, 284]]}
# gained: {"lines": [277, 278, 280, 281, 282, 284, 285, 286, 288, 289, 290], "branches": [[281, 282], [281, 284]]}

import pytest
from click.exceptions import FileError
from click.utils import format_filename
from gettext import gettext as _

class TestFileError:
    def test_file_error_init_with_hint(self):
        """Test FileError initialization with a custom hint."""
        filename = "test_file.txt"
        hint = "Permission denied"
        error = FileError(filename, hint)
        
        assert error.filename == filename
        assert error.ui_filename == format_filename(filename)
        assert error.message == hint
        assert str(error) == hint

    def test_file_error_init_without_hint(self):
        """Test FileError initialization without a hint (default to 'unknown error')."""
        filename = "test_file.txt"
        error = FileError(filename)
        
        assert error.filename == filename
        assert error.ui_filename == format_filename(filename)
        assert error.message == _("unknown error")
        assert str(error) == _("unknown error")

    def test_file_error_format_message(self):
        """Test FileError format_message method."""
        filename = "test_file.txt"
        hint = "File not found"
        error = FileError(filename, hint)
        
        expected_message = _("Could not open file {filename!r}: {message}").format(
            filename=format_filename(filename),
            message=hint
        )
        
        assert error.format_message() == expected_message

    def test_file_error_format_message_with_default_hint(self):
        """Test FileError format_message method with default hint."""
        filename = "test_file.txt"
        error = FileError(filename)
        
        expected_message = _("Could not open file {filename!r}: {message}").format(
            filename=format_filename(filename),
            message=_("unknown error")
        )
        
        assert error.format_message() == expected_message
