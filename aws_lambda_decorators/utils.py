import keyword


def full_name(class_type):
    module = class_type.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return class_type.__class__.__name__  # Avoid reporting __builtin__
    return module + '.' + class_type.__class__.__name__


def is_type_in_list(item_type, items):
    return any(isinstance(item, item_type) for item in items)


def is_valid_variable_name(name):
    return name.isidentifier() and not keyword.iskeyword(name)
