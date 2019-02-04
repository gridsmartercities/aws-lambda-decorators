"""Validation rules for extracted parameter validation."""
import re


class Mandatory:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if the given mandatory variable exists."""

    @staticmethod
    def validate(value=None):
        """
        Check if the given mandatory variable exists.

        Args:
            value (any): Value to be validated.
        """
        return value is not None


class ValidRegex:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if the given variable matches the given regular expression."""

    def __init__(self, regex=''):
        """
        Compile the given regular expression to regular expression pattern.

        Args:
            regex (str): Regular expression for parameter validation.
        """
        self._regexp = re.compile(regex)

    def validate(self, value=None):
        """
        Check if the given variable adheres to the defined regular expression.

        Args:
            value (any): Value to be validated.
        """
        return self._regexp.search(value) is not None
