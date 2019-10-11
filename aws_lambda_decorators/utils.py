"""Utility functions."""
import logging
import os
import json
from http import HTTPStatus
import keyword
import inspect


LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger


def full_name(class_type):
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


def is_type_in_list(item_type, items):
    """
    Checks if there is an item of a given type in the list of items.

    Args:
        item_type (type): the type of the item.
        items (list): a list of items.

    Returns:
        true if an item of the given type exists in the list, otherwise false.
    """
    return any(isinstance(item, item_type) for item in items)


def is_valid_variable_name(name):
    """
    Check if the given name is python allowed variable name.

    Args:
        name (str): the name to check.

    Returns:
        true if the name can be used as a python variable name.
    """
    return name.isidentifier() and not keyword.iskeyword(name)


def all_func_args(func, args, kwargs):
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


def find_key_case_insensitive(key_name, the_dict):
    """
    Finds if a dictionary (the_dict) has a string key (key_name) in any string case

    Args:
        key_name: the key to search in the dictionary
        the_dict: the dictionary to search

    Returns:
        The found key name in its original case, if found. Otherwise, returns the searching key name

    """
    for key in the_dict:
        if key.lower() == key_name:
            return key
    return key_name


def failure(errors, status_code=HTTPStatus.BAD_REQUEST):
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
