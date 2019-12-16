"""Validation rules."""
import datetime
import re
from typing import Any

from schema import Schema, SchemaError


CURRENCIES = {"LKR", "ETB", "RWF", "NZD", "SBD", "MKD", "NPR", "LAK", "KWD", "INR", "HUF", "AFN", "BTN", "ISK", "MVR",
              "WST", "MNT", "AZN", "SAR", "JMD", "BIF", "BMD", "CAD", "GEL", "MXN", "BHD", "HKD", "RSD", "PKR", "SLL",
              "NGN", "TOP", "SCR", "SVC", "CHW", "UYW", "IDR", "IQD", "THB", "GBP", "MYR", "SDG", "CNY", "GNF", "LRD",
              "KHR", "TJS", "BYN", "SHP", "AED", "BOB", "CUC", "PHP", "SSP", "USN", "MZN", "COP", "SEK", "EUR", "CDF",
              "CRC", "KMF", "JPY", "ZWL", "ALL", "GHS", "GIP", "QAR", "GYD", "HTG", "VUV", "CZK", "ANG", "AWG", "AMD",
              "DOP", "TRY", "ZMW", "MGA", "KZT", "XUA", "ARS", "XPF", "BRL", "MXV", "LSL", "CLP", "KES", "PYG", "TND",
              "MAD", "DZD", "MWK", "BSD", "BBD", "FKP", "KGS", "BWP", "CVE", "HRK", "DKK", "COU", "SYP", "LYD", "PLN",
              "TZS", "KPW", "UGX", "BOV", "UAH", "NAD", "AOA", "VES", "SOS", "CUP", "SGD", "PAB", "UZS", "STN", "SRD",
              "CHE", "XOF", "DJF", "PGK", "UYI", "XCD", "BZD", "EGP", "ERN", "RON", "TWD", "USD", "FJD", "VND", "SZL",
              "BND", "HNL", "KRW", "XAF", "MDL", "BDT", "MUR", "PEN", "OMR", "NIO", "TMT", "YER", "TTD", "GMD", "XDR",
              "CHF", "NOK", "GTQ", "JOD", "KYD", "UYU", "RUB", "ZAR", "AUD", "BGN", "MOP", "LBP", "MRU", "CLF", "XSU",
              "BAM", "MMK", "IRR", "ILS"}


class Validator:  # noqa: pylint - too-few-public-methods
    """Validation rule to check if the given mandatory value exists."""
    ERROR_MESSAGE = "Unknown error"

    def __init__(self, error_message: str, condition: Any = None):
        """
        Validates a parameter

        Args:
            error_message (str): A custom error message to output if validation fails
            condition (any): A condition to validate
        """
        self._error_message = error_message or self.ERROR_MESSAGE
        self._condition = condition

    def message(self, value: Any = None) -> str:
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
    ERROR_MESSAGE = "Missing mandatory value"

    def __init__(self, error_message: str = None):
        """
        Checks if a parameter has a value

        Args:
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message)

    @staticmethod
    def validate(value: Any = None) -> bool:
        """
        Check if the given mandatory value exists.

        Args:
            value (any): Value to be validated.
        """
        return value is not None and str(value)


class RegexValidator(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value matches a regular expression."""
    ERROR_MESSAGE = "'{value}' does not conform to regular expression '{condition}'"

    def __init__(self, regex: str = "", error_message: str = None):
        """
        Compile a regular expression to a regular expression pattern.

        Args:
            regex (str): Regular expression for parameter validation.
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, regex)
        self._regexp = re.compile(regex)

    def validate(self, value: str = None) -> bool:
        """
        Check if a value adheres to the defined regular expression.

        Args:
            value (str): Value to be validated.
        """
        if value is None:
            return True

        return self._regexp.fullmatch(value) is not None


class SchemaValidator(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value matches a regular expression."""
    ERROR_MESSAGE = "'{value}' does not validate against schema '{condition}'"

    def __init__(self, schema: Schema, error_message: str = None):
        """
        Set the schema field.

        Args:
            schema (Schema): The expected schema.
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, schema)

    def validate(self, value: Any = None) -> bool:
        """
        Check if the object adheres to the defined schema.

        Args:
            value (object): Value to be validated.
        """
        try:
            if value is None:
                return True

            return self._condition.validate(value) == value
        except SchemaError:
            return False


class Minimum(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if a value is greater than a minimum value."""
    ERROR_MESSAGE = "'{value}' is less than minimum value '{condition}'"

    def __init__(self, minimum: (float, int), error_message: str = None):
        """
        Set the minimum value.

        Args:
            minimum (float, int): The minimum value.
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, minimum)

    def validate(self, value: (float, int) = None) -> bool:  # pylint:disable=bad-whitespace
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
    ERROR_MESSAGE = "'{value}' is greater than maximum value '{condition}'"

    def __init__(self, maximum: (float, int), error_message: str = None):
        """
        Set the maximum value.

        Args:
            maximum (float, int): The maximum value.
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, maximum)

    def validate(self, value: (float, int) = None) -> bool:  # pylint:disable=bad-whitespace
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
    ERROR_MESSAGE = "'{value}' is shorter than minimum length '{condition}'"

    def __init__(self, min_length: int, error_message: str = None):
        """
        Set the minimum length.

        Args:
            min_length (int): The minimum length.
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, min_length)

    def validate(self, value: str = None) -> bool:
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
    ERROR_MESSAGE = "'{value}' is longer than maximum length '{condition}'"

    def __init__(self, max_length: int, error_message: str = None):
        """
        Set the maximum length.

        Args:
            max_length (int): The maximum length.
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, max_length)

    def validate(self, value: str = None) -> bool:
        """
        Check if a string is longer than the maximum length.

        Args:
            value (str): String to be validated.
        """
        if value is None:
            return True

        return len(str(value)) <= self._condition


class Type(Validator):
    ERROR_MESSAGE = "'{value}' is not of type '{condition.__name__}'"

    def __init__(self, valid_type: type, error_message: str = None):
        """
        Set the valid type.

        Args:
            valid_type (type): The value type to check.
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, valid_type)

    def validate(self, value: Any = None) -> bool:
        """
        Check if a value is of the right type

        Args:
            value (object): object to be validated.
        """
        if value is None:
            return True

        return isinstance(value, self._condition)


class EnumValidator(Validator):
    ERROR_MESSAGE = "'{value}' is not in list '{condition}'"

    def __init__(self, *args: list, error_message: str = None):
        """
        Set the list of valid values.

        Args:
            error_message (str): A custom error message to output if validation fails
            args (list): The list of valid values
        """
        super().__init__(error_message, args)

    def validate(self, value: Any = None) -> bool:
        """
        Check if a value is in a list of valid values

        Args:
            value (object): object to be validated.
        """
        if value is None:
            return True

        return value in self._condition


class NonEmpty(Validator):  # noqa: pylint - too-few-public-methods
    """Validation rule to check if the given value is empty."""
    ERROR_MESSAGE = "Value is empty"

    def __init__(self, error_message: str = None):
        """
        Checks if a parameter has a non empty value

        Args:
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message)

    @staticmethod
    def validate(value: Any = None) -> bool:
        """
        Check if the given value is non empty.

        Args:
            value (any): Value to be validated.
        """
        if value is None or value in (0, 0.0, 0j):
            return True

        return bool(value)


class DateValidator(Validator):
    """Validation rule to check if a string is a valid date according to some format."""
    ERROR_MESSAGE = "'{value}' is not a '{condition}' date"

    def __init__(self, date_format: str, error_message: str = None):
        """
        Checks if a string is a date with a given format

        Args:
            date_format (str): The date format to check against
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message, date_format)

    def validate(self, value: str = None) -> bool:
        """
        Check if a string is a date with a given format

        Args:
            value (str): string date to validate against a format
        """
        if value is None:
            return True

        try:
            datetime.datetime.strptime(value, self._condition)
        except ValueError:
            return False
        else:
            return True


class CurrencyValidator(Validator):
    """Validation rule to check if a string is a valid currency according to ISO 4217 Currency Code."""
    ERROR_MESSAGE = "'{value}' is not a valid currency code."

    def __init__(self, error_message: str = None):
        """
        Checks if a string is a valid currency based on ISO 4217

        Args:
            error_message (str): A custom error message to output if validation fails
        """
        super().__init__(error_message)

    @staticmethod
    def validate(value: str = None) -> bool:
        """
        Check if a string is a valid currency based on ISO 4217

        Args:
            value (str): value to validate against a ISO 4217
        """

        if value is None:
            return True

        return value.upper() in CURRENCIES
