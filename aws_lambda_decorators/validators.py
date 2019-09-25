"""Validation rules."""
import re
from schema import SchemaError


class Validator:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if the given mandatory value exists."""

    def __init__(self, error_message, condition=None):
        """
        Validates a parameter

        Args:
            error_message (str): A custom error message to output if validation fails
            condition (any): A condition to validate
        """
        self._error_message = error_message
        self._condition = condition

    def message(self, value=None):  # noqa: pylint - unused-argument
        """
        Gets the formatted error message for a failed mandatory check

        Args:
            value (any): The validated value

        Returns:
            The error message
        """
        return self._error_message.format(value=value, condition=self._condition)


class Mandatory(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if the given mandatory value exists."""

    def __init__(self, error_message=None):
        """
        Checks if a parameter has a value

        Args:
            error_message (str): A custom error message to output if validation fails
        """
        Validator.__init__(self, error_message or "Missing mandatory value")

    @staticmethod
    def validate(value=None):
        """
        Check if the given mandatory value exists.

        Args:
            value (any): Value to be validated.
        """
        return value is not None


class RegexValidator(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value matches a regular expression."""

    def __init__(self, regex='', error_message=None):
        """
        Compile a regular expression to a regular expression pattern.

        Args:
            regex (str): Regular expression for parameter validation.
            error_message (str): A custom error message to output if validation fails
        """
        Validator.__init__(
            self, error_message or "'{value}' does not conform to regular expression '{condition}'", regex)
        self._regexp = re.compile(regex)

    def validate(self, value=None):
        """
        Check if a value adheres to the defined regular expression.

        Args:
            value (str): Value to be validated.
        """
        return self._regexp.fullmatch(value) is not None


class SchemaValidator(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value matches a regular expression."""

    def __init__(self, schema, error_message=None):
        """
        Set the schema field.

        Args:
            schema (Schema): The expected schema.
            error_message (str): A custom error message to output if validation fails
        """
        Validator.__init__(self, error_message or "'{value}' does not validate against schema '{condition}'", schema)

    def validate(self, value=None):
        """
        Check if the object adheres to the defined schema.

        Args:
            value (object): Value to be validated.
        """
        try:
            return self._condition.validate(value) == value
        except SchemaError:
            return False


class Minimum(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value is greater than a minimum value."""

    def __init__(self, minimum: (float, int), error_message=None):
        """
        Set the minimum value.

        Args:
            minimum (float, int): The minimum value.
            error_message (str): A custom error message to output if validation fails
        """
        Validator.__init__(self, error_message or "'{value}' is less than minimum value '{condition}'", minimum)

    def validate(self, value=None):
        """
        Check if the value is greater than the minimum.

        Args:
            value (float, int): Value to be validated.
        """
        if value is None:
            return True

        if isinstance(value, (float, int)):
            return self._condition <= value

        return False


class Maximum(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value is less than a maximum value."""

    def __init__(self, maximum: (float, int), error_message=None):
        """
        Set the maximum value.

        Args:
            maximum (float, int): The maximum value.
            error_message (str): A custom error message to output if validation fails
        """
        Validator.__init__(self, error_message or "'{value}' is greater than maximum value '{condition}'", maximum)

    def validate(self, value=None):
        """
        Check if the value is less than the maximum.

        Args:
            value (float, int): Value to be validated.
        """
        if value is None:
            return True

        if isinstance(value, (float, int)):
            return self._condition >= value

        return False


class MinLength(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a string is shorter than a minimum length."""

    def __init__(self, min_length: int, error_message=None):
        """
        Set the minimum length.

        Args:
            min_length (int): The minimum length.
            error_message (str): A custom error message to output if validation fails
        """
        Validator.__init__(
            self, error_message or "'{value}' is shorter than minimum length '{condition}'", min_length)

    def validate(self, value=None):
        """
        Check if a string is shorter than the minimum length.

        Args:
            value (str): String to be validated.
        """
        if value is None:
            return True

        return len(str(value)) >= self._condition


class MaxLength(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a string is longer than a maximum length."""

    def __init__(self, max_length: int, error_message=None):
        """
        Set the maximum length.

        Args:
            max_length (int): The maximum length.
            error_message (str): A custom error message to output if validation fails
        """
        Validator.__init__(self, error_message or "'{value}' is longer than maximum length '{condition}'", max_length)

    def validate(self, value=None):
        """
        Check if a string is longer than the maximum length.

        Args:
            value (str): String to be validated.
        """
        if value is None:
            return True

        return len(str(value)) <= self._condition
