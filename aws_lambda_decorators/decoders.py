"""Decoder abstractions and functions for decoding/converting a string of a given annotation to a dictionary."""
import json
import logging
import sys
import jwt

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

DECODE_FUNC_NAME = 'decode_%s'
DECODE_FUNC_MISSING_ERROR = 'Missing decode function for annotation: %s'


def decode(annotation, value):
    """
    Convert the given string from an annotation to a python dictionary.

    If :annotation: is not empty, use decode_:annotation:(:value:) to convert to dictionary.

    Args:
        annotation (str): the type of encoding of the value (e.g. 'json', 'jwt').
        value (str): the value to be converted from given annotation to a dictionary.

    Return:
        decoded dictionary.
    """
    if annotation:
        module_name = sys.modules[__name__]
        func_name = DECODE_FUNC_NAME % annotation
        if hasattr(module_name, func_name):
            func = getattr(module_name, func_name)
            return func(value)

        LOGGER.error(DECODE_FUNC_MISSING_ERROR, annotation)

    return value


def decode_json(value):
    """Convert a json to a dictionary."""
    return json.loads(value)


def decode_jwt(value):
    """Convert a jwt to a dictionary."""
    return jwt.decode(value, verify=False)
