"""Decoder abstractions and functions for decoding/converting a string with a given annotation to a dictionary."""
import functools
import json
import logging
import sys
import jwt

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

DECODE_FUNC_NAME = "decode_%s"
DECODE_FUNC_MISSING_ERROR = "Missing decode function for annotation: %s"


def decode(annotation, value):
    """
    Converts an annotated string to a python dictionary.

    If :annotation: is not empty, use decode_:annotation:(:value:) to convert to dictionary.

    Existing decoders:
         annotation     decoder
          [json]      decode_json
          [jwt]       decode_jwt
           [n]        where n is a number. Decodes the value as an array, and picks item n from the array

    Args:
        annotation (str): the type of encoding of the value (e.g. 'json', 'jwt').
        value (str): the value to be converted from given annotation to a dictionary.

    Returns:
        decoded dictionary.
    """
    if annotation:
        if annotation.isdigit():
            return value[int(annotation)]

        module_name = sys.modules[__name__]
        func_name = DECODE_FUNC_NAME % annotation
        if hasattr(module_name, func_name):
            func = getattr(module_name, func_name)
            return func(value)

        LOGGER.error(DECODE_FUNC_MISSING_ERROR, annotation)

    return value


@functools.lru_cache()
def decode_json(value):
    """Convert a json to a dictionary."""
    return json.loads(value)


@functools.lru_cache()
def decode_jwt(value):
    """Convert a jwt to a dictionary."""
    return jwt.decode(value, verify=False)
