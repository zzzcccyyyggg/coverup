# file: src/click/src/click/termui.py:197-258
# asked: {"lines": [197, 199, 200, 201, 202, 203, 229, 230, 231, 232, 233, 236, 237, 240, 243, 244, 245, 246, 247, 248, 249, 250, 251, 253, 254, 255, 256, 257, 258], "branches": [[236, 237], [246, 247], [246, 248], [248, 249], [248, 250], [250, 251], [250, 253], [256, 257], [256, 258]]}
# gained: {"lines": [197, 199, 200, 201, 202, 203, 229, 230, 231, 232, 233, 236, 237, 240, 243, 244, 245, 246, 247, 248, 249, 250, 251, 253, 254, 255, 256, 257, 258], "branches": [[236, 237], [246, 247], [246, 248], [248, 249], [248, 250], [250, 251], [250, 253], [256, 257], [256, 258]]}

import pytest
from unittest.mock import Mock, patch
from click.exceptions import Abort
from click.termui import confirm


class TestConfirm:
    """Test cases for click.termui.confirm function to achieve full coverage."""
    
    def test_confirm_with_default_none_and_invalid_input_then_valid(self, monkeypatch):
        """Test confirm with default=None, first invalid input then valid 'yes'."""
        inputs = ["invalid", "yes"]
        mock_input = Mock(side_effect=inputs)
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo") as mock_echo:
            result = confirm("Test question", default=None)
            
        assert result is True
        # Should show error for invalid input
        mock_echo.assert_any_call("Error: invalid input", err=False)
    
    def test_confirm_with_default_none_and_invalid_input_then_no(self, monkeypatch):
        """Test confirm with default=None, first invalid input then valid 'no'."""
        inputs = ["invalid", "no"]
        mock_input = Mock(side_effect=inputs)
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo") as mock_echo:
            result = confirm("Test question", default=None)
            
        assert result is False
        # Should show error for invalid input
        mock_echo.assert_any_call("Error: invalid input", err=False)
    
    def test_confirm_with_default_true_and_empty_input(self, monkeypatch):
        """Test confirm with default=True and empty input."""
        mock_input = Mock(return_value="")
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo"):
            result = confirm("Test question", default=True)
            
        assert result is True
    
    def test_confirm_with_default_false_and_empty_input(self, monkeypatch):
        """Test confirm with default=False and empty input."""
        mock_input = Mock(return_value="")
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo"):
            result = confirm("Test question", default=False)
            
        assert result is False
    
    def test_confirm_with_abort_true_and_no_answer(self, monkeypatch):
        """Test confirm with abort=True and 'no' answer raises Abort."""
        mock_input = Mock(return_value="no")
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo"):
            with pytest.raises(Abort):
                confirm("Test question", abort=True)
    
    def test_confirm_with_abort_true_and_yes_answer_no_abort(self, monkeypatch):
        """Test confirm with abort=True and 'yes' answer does not raise Abort."""
        mock_input = Mock(return_value="yes")
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo"):
            result = confirm("Test question", abort=True)
            
        assert result is True
    
    def test_confirm_with_err_true(self, monkeypatch):
        """Test confirm with err=True parameter."""
        mock_input = Mock(return_value="yes")
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo") as mock_echo:
            result = confirm("Test question", err=True)
            
        assert result is True
        # Verify echo was called with err=True for the prompt
        # Check that at least one call had err=True
        err_true_calls = [call for call in mock_echo.call_args_list 
                         if call.kwargs.get('err') is True]
        assert len(err_true_calls) > 0
    
    def test_confirm_keyboard_interrupt_raises_abort(self, monkeypatch):
        """Test confirm raises Abort on KeyboardInterrupt."""
        mock_input = Mock(side_effect=KeyboardInterrupt)
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo"):
            with pytest.raises(Abort):
                confirm("Test question")
    
    def test_confirm_eof_error_raises_abort(self, monkeypatch):
        """Test confirm raises Abort on EOFError."""
        mock_input = Mock(side_effect=EOFError)
        monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
        
        with patch("click.termui.echo"):
            with pytest.raises(Abort):
                confirm("Test question")
    
    def test_confirm_case_insensitive_yes(self, monkeypatch):
        """Test confirm accepts case-insensitive 'yes' variations."""
        for input_val in ["YES", "Yes", "yEs", "yes"]:
            mock_input = Mock(return_value=input_val)
            monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
            
            with patch("click.termui.echo"):
                result = confirm("Test question")
                
            assert result is True
    
    def test_confirm_case_insensitive_no(self, monkeypatch):
        """Test confirm accepts case-insensitive 'no' variations."""
        for input_val in ["NO", "No", "nO", "no"]:
            mock_input = Mock(return_value=input_val)
            monkeypatch.setattr("click.termui.visible_prompt_func", mock_input)
            
            with patch("click.termui.echo"):
                result = confirm("Test question")
                
            assert result is False
