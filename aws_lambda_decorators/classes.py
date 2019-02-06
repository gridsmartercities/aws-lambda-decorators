"""All the classes used as parameters for the decorators."""
from aws_lambda_decorators.decoders import decode
from aws_lambda_decorators.validators import Mandatory
from aws_lambda_decorators.utils import is_type_in_list, is_valid_variable_name

PATH_DIVIDER = '/'
ANNOTATIONS_START = '['
ANNOTATIONS_END = ']'


class ExceptionHandler:
    """Class mapping an friendly error message to a given Exception."""

    def __init__(self, exception, friendly_message):
        """
        Sets the private variables of the ExceptionHandler object.

        Args:
            exception (object|Exception): An exception to be handled.
            friendly_message (str): Friendly Message to be returned if the exception is caught.
        """
        self._exception = exception
        self._friendly_message = friendly_message

    @property
    def friendly_message(self):
        """Getter for the friendly message parameter."""
        return self._friendly_message

    @property
    def exception(self):
        """Getter for the exception parameter."""
        return self._exception


class Parameter:
    """Class used to encapsulate the extract methods parameters data."""

    def __init__(self, path, validators=None, func_param_index=0, var_name=None):
        """
        Sets the private variables of the Parameter object.

        Args:
            path (str): The path to the variable we want to extract. Can use any annotation that has an existing
                equivalent decode function in decoders.py (like [jwt] or [json]).
                As an example, given the dictionary

                {
                    "a": {
                        "b": "{ 'c': 'hello' }",
                    }
                }

                the path to c is "a/b[json]/c"
            validators (list): A list of validators the value must conform to (e.g. Mandatory(), ValidRegex(my_regex).
            func_param_index (int): Optional, the index for the dictionary in the function signature e.g.:
                def fun(event, context), to extract from context func_param_index has to be 1.
            var_name (str): Optional, the name of the variable we want to assign the extracted value to. The default
                value is the last element of the path (e.g. 'c' in the case above)
        """
        self._func_param_index = func_param_index
        self._path = path
        self._validators = validators
        self._name = var_name

    @property
    def func_param_index(self):
        """Getter for the func_param_index parameter."""
        return self._func_param_index

    @property
    def path(self):
        """Getter for the path parameter."""
        return self._path

    @func_param_index.setter
    def func_param_index(self, value):
        """Setter for the func_param_index parameter."""
        self._func_param_index = value

    def get_value_by_path(self, args):
        """
        Calculate and decode the value of the variable in the given path.

        Used by the decorators.

        Args:
            args (list): list of arguments passed by the decorator. Used for extracting from a given dictionary at
                args[func_param_index]

        Raises:
            KeyError: if the parameter does not validate.
        """
        dict_value = args[self._func_param_index]

        for path_key in filter(lambda item: item != '', self.path.split(PATH_DIVIDER)):
            real_key, annotation = Parameter.get_annotations_from_key(path_key)
            if real_key in dict_value:
                dict_value = decode(annotation, dict_value[real_key])
            elif self._validators and is_type_in_list(Mandatory, self._validators):
                raise KeyError(real_key)

        val = dict_value.get(real_key, None) if isinstance(dict_value, dict) else dict_value
        if not self.validate(val):
            raise KeyError(real_key)

        if not self._name:
            self._name = real_key
        return dict_value

    def validate(self, value):
        """Check if the given value adheres to the given validation rules."""
        if not self._validators:
            return True
        for validator in self._validators:
            if not validator.validate(value):
                return False
        return True

    def get_var_name(self):
        """
        Getter for the var_name parameter.

        Raises:
            SyntaxError: if the name is set and is not a valid python variable name
        """
        if self._name and not is_valid_variable_name(self._name):
            raise SyntaxError(self._name)
        return self._name

    @staticmethod
    def get_annotations_from_key(key):
        """
        Extract the key and the encoding type (annotation) from the string.

        Args:
            key (str): a combined string to extract key and annotation from. e.g. ('key[jwt]' -> 'key', 'jwt',
                                                                                   'key'      -> 'key', None)
        """
        if ANNOTATIONS_START in key and ANNOTATIONS_END in key:
            annotation = key[key.find(ANNOTATIONS_START) + 1:key.find(ANNOTATIONS_END)]
            return key.replace(ANNOTATIONS_START + annotation + ANNOTATIONS_END, ''), annotation
        return key, None


class SSMParameter:
    """Object used for defining the key and, optionally, the variable name for ssm parameter extraction."""

    def __init__(self, ssm_name, var_name=None):
        """
        Set the private variables of the SSMParameter object.

        Args:
            ssm_name (str): Key of the variable in the AWS parameter store
            var_name (str): Optional, the name of variable to store the extracted value to. Defaults to the ssm_name.
        """
        self._ssm_name = ssm_name
        self._name = var_name if var_name else ssm_name

    def get_ssm_name(self):
        """Getter for the ssm_name parameter."""
        return self._ssm_name

    def get_var_name(self):
        """Getter for the var_name parameter."""
        if self._name and not is_valid_variable_name(self._name):
            raise SyntaxError(self._name)
        return self._name
