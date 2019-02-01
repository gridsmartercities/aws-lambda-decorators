import re


class Mandatory:  # noqa: pylint - too-few-public-methods
    @staticmethod
    def validate(value=None):
        return value is not None


class ValidRegex:  # noqa: pylint - too-few-public-methods
    def __init__(self, regex=''):
        self._regexp = re.compile(regex)

    def validate(self, value=None):
        return self._regexp.search(value) is not None
