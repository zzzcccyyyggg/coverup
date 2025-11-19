# file: src/click/src/click/testing.py:69-85
# asked: {"lines": [69, 70, 75, 76, 77, 79, 80, 81, 83, 84, 85], "branches": []}
# gained: {"lines": [69, 70, 75, 76, 77, 79, 80, 81, 83, 84, 85], "branches": []}

import pytest
import io
from click.testing import BytesIOCopy


class TestBytesIOCopy:
    def test_init(self):
        """Test that BytesIOCopy initializes correctly with copy_to parameter."""
        copy_to = io.BytesIO()
        bio_copy = BytesIOCopy(copy_to)
        
        assert bio_copy.copy_to is copy_to
        assert bio_copy.getvalue() == b""

    def test_write(self):
        """Test that write method writes to both the main stream and copy_to stream."""
        copy_to = io.BytesIO()
        bio_copy = BytesIOCopy(copy_to)
        
        test_data = b"hello world"
        result = bio_copy.write(test_data)
        
        assert result == len(test_data)
        assert bio_copy.getvalue() == test_data
        assert copy_to.getvalue() == test_data

    def test_flush(self):
        """Test that flush method flushes both the main stream and copy_to stream."""
        copy_to = io.BytesIO()
        bio_copy = BytesIOCopy(copy_to)
        
        # Write some data first
        bio_copy.write(b"test data")
        
        # Mock the flush methods to verify they are called
        main_flush_called = False
        copy_flush_called = False
        
        original_main_flush = bio_copy.flush
        original_copy_flush = copy_to.flush
        
        def mock_main_flush():
            nonlocal main_flush_called
            main_flush_called = True
            original_main_flush()
        
        def mock_copy_flush():
            nonlocal copy_flush_called
            copy_flush_called = True
            original_copy_flush()
        
        bio_copy.flush = mock_main_flush
        copy_to.flush = mock_copy_flush
        
        bio_copy.flush()
        
        assert main_flush_called
        assert copy_flush_called

    def test_multiple_writes(self):
        """Test that multiple writes work correctly with both streams."""
        copy_to = io.BytesIO()
        bio_copy = BytesIOCopy(copy_to)
        
        data1 = b"first "
        data2 = b"second"
        data3 = b" third"
        
        result1 = bio_copy.write(data1)
        result2 = bio_copy.write(data2)
        result3 = bio_copy.write(data3)
        
        assert result1 == len(data1)
        assert result2 == len(data2)
        assert result3 == len(data3)
        
        expected_total = data1 + data2 + data3
        assert bio_copy.getvalue() == expected_total
        assert copy_to.getvalue() == expected_total

    def test_empty_write(self):
        """Test writing empty bytes."""
        copy_to = io.BytesIO()
        bio_copy = BytesIOCopy(copy_to)
        
        result = bio_copy.write(b"")
        
        assert result == 0
        assert bio_copy.getvalue() == b""
        assert copy_to.getvalue() == b""
