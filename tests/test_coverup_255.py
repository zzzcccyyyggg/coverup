# file: src/flask/src/flask/cli.py:1122-1123
# asked: {"lines": [1122, 1123], "branches": []}
# gained: {"lines": [1122, 1123], "branches": []}

import pytest
from flask.cli import main as flask_cli_main
from unittest.mock import patch
import sys

def test_main_function_executes():
    """Test that the main() function calls cli.main() and executes successfully."""
    # The main() function calls cli.main() which is a Click command
    # When called with no arguments, it exits with code 2 (usage error)
    # We just need to verify that the function executes without raising exceptions
    # other than the expected SystemExit from Click
    
    with pytest.raises(SystemExit) as exc_info:
        flask_cli_main()
    
    # The main function should exit with status 2 when called with no arguments
    # (this is Click's standard behavior for missing required arguments)
    assert exc_info.value.code == 2

def test_main_function_with_help_flag():
    """Test that main() function works correctly when help flag is passed."""
    # We need to simulate passing the --help flag to the CLI
    # This requires patching sys.argv to include the help flag
    
    with patch.object(sys, 'argv', ['flask', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            flask_cli_main()
        
        # When help is requested, Click should exit with status 0
        assert exc_info.value.code == 0
