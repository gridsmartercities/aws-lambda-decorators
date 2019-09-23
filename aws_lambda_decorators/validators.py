"""Validation rules."""
import re
from schema import SchemaError


class Mandatory:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if the given mandatory value exists."""

    @staticmethod
    def validate(value=None):
        """
        Check if the given mandatory value exists.

        Args:
            value (any): Value to be validated.
        """
        return value is not None

    @staticmethod
    def message(value=None):  # noqa: pylint - unused-argument
        """
        Gets the formatted error message for a failed mandatory check

        Args:
            value (any): The validated value

        Returns:
            The error message
        """
        return "Missing mandatory value"


class RegexValidator:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value matches a regular expression."""

    def __init__(self, regex=''):
        """
        Compile a regular expression to a regular expression pattern.

        Args:
            regex (str): Regular expression for parameter validation.
        """
        self._regex = regex
        self._regexp = re.compile(regex)

    def validate(self, value=None):
        """
        Check if a value adheres to the defined regular expression.

        Args:
            value (str): Value to be validated.
        """
        return self._regexp.fullmatch(value) is not None

    def message(self, value=None):
        """
        Gets the formatted error message for a failed regex check

        Args:
            value (any): The validated value

        Returns:
            The error message
        """
        return f"{value} does not conform to regular expression {self._regex}"


class SchemaValidator:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value matches a regular expression."""

    def __init__(self, schema):
        """
        Set the schema field.

        Args:
            schema (Schema): The expected schema.
        """
        self._schema = schema

    def validate(self, value=None):
        """
        Check if the object adheres to the defined schema.

        Args:
            value (object): Value to be validated.
        """
        try:
            return self._schema.validate(value) == value
        except SchemaError:
            return False

    def message(self, value=None):
        """
        Gets the formatted error message for a failed schema check

        Args:
            value (dict): The validated value

        Returns:
            The error message
        """
        return f"{value} does not validate against schema {self._schema}"


class Minimum:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value is greater than a minimum value."""

    def __init__(self, minimum: (float, int)):
        """
        Set the minimum value.

        Args:
            minimum (float, int): The minimum value.
        """
        self._minimum = minimum

    def validate(self, value=None):
        """
        Check if the value is greater than the minimum.

        Args:
            value (float, int): Value to be validated.
        """
        if value is None:
            return True

        if isinstance(value, (float, int)):
            return self._minimum <= value

        return False

    def message(self, value=None):
        """
        Gets the formatted error message for a failed minimum value check

        Args:
            value (int): The validated value

        Returns:
            The error message
        """
        return f"{value} is smaller than minimum value ({self._minimum})"


class Maximum:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value is less than a maximum value."""

    def __init__(self, maximum: (float, int)):
        """
        Set the maximum value.

        Args:
            maximum (float, int): The maximum value.
        """
        self._maximum = maximum

    def validate(self, value=None):
        """
        Check if the value is less than the maximum.

        Args:
            value (float, int): Value to be validated.
        """
        if value is None:
            return True

        if isinstance(value, (float, int)):
            return self._maximum >= value

        return False

    def message(self, value=None):
        """
        Gets the formatted error message for a failed maximum value check

        Args:
            value (int): The validated value

        Returns:
            The error message
        """
        return f"{value} is bigger than maximum value ({self._maximum})"
