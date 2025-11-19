# file: src/click/src/click/core.py:3347-3351
# asked: {"lines": [3347, 3348, 3349, 3350, 3351], "branches": [[3349, 3350], [3349, 3351]]}
# gained: {"lines": [3347, 3348, 3349, 3350, 3351], "branches": [[3349, 3350], [3349, 3351]]}

import pytest
import click
from click.core import Argument


class TestArgumentHumanReadableName:
    def test_human_readable_name_with_metavar(self):
        """Test that human_readable_name returns metavar when set."""
        arg = Argument(["test_arg"], metavar="CUSTOM_METAVAR")
        assert arg.human_readable_name == "CUSTOM_METAVAR"

    def test_human_readable_name_without_metavar(self):
        """Test that human_readable_name returns uppercase name when metavar is None."""
        arg = Argument(["test_arg"])
        assert arg.human_readable_name == "TEST_ARG"
