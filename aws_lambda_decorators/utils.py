"""Utility functions."""

from functools import lru_cache
from http import HTTPStatus
import inspect
import json
import keyword
import logging
from logging import Logger
import os
from typing import Any, Callable, Dict, List
from unicodedata import normalize as normalise

import boto3


LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger


def full_name(class_type: type) -> str:
    """
    Gets the fully qualified name of a class type.

    From https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python

    Args:
        class_type (type): the type of the class.

    Returns:
        the fully qualified name of the class type.
    """
    module = class_type.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return class_type.__class__.__name__  # Avoid reporting __builtin__
    return f"{module}.{class_type.__class__.__name__}"


def is_type_in_list(item_type: type, items: list) -> bool:
    """
    Checks if there is an item of a given type in the list of items.

    Args:
        item_type (type): the type of the item.
        items (list): a list of items.

    Returns:
        true if an item of the given type exists in the list, otherwise false.
    """
    return any(isinstance(item, item_type) for item in items)


def is_valid_variable_name(name: str) -> bool:
    """
    Check if the given name is python allowed variable name.

    Args:
        name (str): the name to check.

    Returns:
        true if the name can be used as a python variable name.
    """
    return name.isidentifier() and not keyword.iskeyword(name)


def all_func_args(func: Callable, args: list, kwargs: dict) -> dict:
    """
    Combine arguments and key word arguments to a dictionary.

    Args:
        func (function): function whose arguments should be extracted.
        args (list): list of function args (*args).
        kwargs (dict): dictionary of function kwargs (**kwargs).

    Returns:
        dictionary argument name -> argument value.
    """
    arg_spec = inspect.getfullargspec(func)[0]
    arg_dictionary = {arg_spec[idx]: value for idx, value in enumerate(args)}
    arg_dictionary.update(kwargs)
    return arg_dictionary


def find_key_case_insensitive(key_name: str, the_dict: Dict[str, Any]) -> str:
    """
    Finds if a dictionary (the_dict) has a string key (key_name) in any string case

    Args:
        key_name: the key to search in the dictionary
        the_dict: the dictionary to search

    Returns:
        The found key name in its original case, if found. Otherwise, returns the searching key name

    """
    def desensitise(txt: str) -> str:
        return normalise("NFC", txt).casefold()

    key_name_lower = desensitise(key_name)

    for key in the_dict:
        if desensitise(key) == key_name_lower:
            return key

    return key_name


def failure(errors: List[str], status_code: int = HTTPStatus.BAD_REQUEST) -> dict:
    """
    Returns an error to the caller

    Args:
        errors (list): a list of errors to be returned
        status_code (int): the status code of the error

    Returns:
        An object that contains the status code and the list of errors
    """
    return {
        "statusCode": status_code,
        "body": json.dumps({"message": errors})
    }


def find_websocket_connection_id(args: list) -> str:
    """
    Finds an API Gateway connection id from the event dictionary in the
    arguments of a lambda

    Args:
        args (list): a list of arguments from a lambda (*args)

    Returns:
        The connection id of a user as a string if found
        None if not
    """
    for arg in args:
        if isinstance(arg, dict) and "requestContext" in arg:
            return arg["requestContext"].get("connectionId")
    return None


@lru_cache()
def get_websocket_endpoint(endpoint_url: str) -> "botocore.client.ApiGatewayManagementApi":  # noqa: pyflakes - F821
    """
    Gets an instance of ApiGatewayManagementApi for sending messages
    through websockets

    Args:
        endpoint_url (str): an api gateway connection url (ish)

    Returns:
        The api gateway management client (cached)
    """
    return boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=endpoint_url
    )
