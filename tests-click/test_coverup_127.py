# file: src/click/src/click/testing.py:88-111
# asked: {"lines": [88, 89, 96, 97, 98, 99, 101, 109, 110, 111], "branches": []}
# gained: {"lines": [88, 89, 96, 97, 98, 99, 101, 109, 110, 111], "branches": []}

import pytest
import io
from click.testing import StreamMixer, BytesIOCopy

class TestStreamMixer:
    def test_stream_mixer_initialization(self):
        """Test that StreamMixer initializes with correct attributes."""
        mixer = StreamMixer()
        
        assert isinstance(mixer.output, io.BytesIO)
        assert isinstance(mixer.stdout, BytesIOCopy)
        assert isinstance(mixer.stderr, BytesIOCopy)
        assert mixer.stdout.copy_to is mixer.output
        assert mixer.stderr.copy_to is mixer.output

    def test_stream_mixer_del_calls_close(self, monkeypatch):
        """Test that __del__ method properly closes all streams."""
        mixer = StreamMixer()
        
        # Track which close methods are called
        close_calls = []
        
        def mock_close(stream_name):
            def _close():
                close_calls.append(stream_name)
            return _close
        
        # Mock the close methods to track calls
        monkeypatch.setattr(mixer.stderr, 'close', mock_close('stderr'))
        monkeypatch.setattr(mixer.stdout, 'close', mock_close('stdout'))
        monkeypatch.setattr(mixer.output, 'close', mock_close('output'))
        
        # Call __del__ directly
        mixer.__del__()
        
        # Verify close was called in the correct order
        assert close_calls == ['stderr', 'stdout', 'output']

    def test_stream_mixer_del_handles_already_closed_streams(self):
        """Test that __del__ handles streams that are already closed."""
        mixer = StreamMixer()
        
        # Close streams first
        mixer.stderr.close()
        mixer.stdout.close()
        mixer.output.close()
        
        # This should not raise any exceptions
        mixer.__del__()

    def test_stream_mixer_context_management(self):
        """Test that StreamMixer can be used in a context manager pattern."""
        mixer = StreamMixer()
        
        # Write to streams
        mixer.stdout.write(b"stdout data")
        mixer.stderr.write(b"stderr data")
        
        # Verify data was copied to output
        output_data = mixer.output.getvalue()
        assert b"stdout data" in output_data
        assert b"stderr data" in output_data
        
        # Clean up by calling __del__
        mixer.__del__()
        
        # Verify streams are closed
        assert mixer.stderr.closed
        assert mixer.stdout.closed
        assert mixer.output.closed
