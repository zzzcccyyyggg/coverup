# file: src/click/src/click/types.py:424-429
# asked: {"lines": [424, 425], "branches": []}
# gained: {"lines": [424, 425], "branches": []}

import pytest
from click.types import DateTime
import collections.abc as cabc


class TestDateTime:
    def test_init_with_none_formats(self):
        """Test that DateTime uses default formats when None is provided."""
        dt = DateTime()
        expected_formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]
        assert dt.formats == expected_formats
        assert isinstance(dt.formats, cabc.Sequence)

    def test_init_with_custom_formats(self):
        """Test that DateTime uses provided formats when not None."""
        custom_formats = ["%Y-%m-%d", "%d/%m/%Y"]
        dt = DateTime(formats=custom_formats)
        assert dt.formats == custom_formats
        assert isinstance(dt.formats, cabc.Sequence)
