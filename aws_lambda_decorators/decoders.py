import json
import logging
import sys
import jwt

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

DECODE_FUNC_NAME = 'decode_%s'
DECODE_FUNC_MISSING_ERROR = 'Missing decode function for annotation: %s'


def decode(annotation, value):
    if annotation:
        module_name = sys.modules[__name__]
        func_name = DECODE_FUNC_NAME % annotation
        if hasattr(module_name, func_name):
            func = getattr(module_name, func_name)
            return func(value)

        LOGGER.error(DECODE_FUNC_MISSING_ERROR % annotation)

    return value


def decode_json(value):
    return json.loads(value)


def decode_jwt(value):
    return jwt.decode(value, verify=False)
