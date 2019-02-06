"""Utility functions."""
import keyword


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
    return module + '.' + class_type.__class__.__name__


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
