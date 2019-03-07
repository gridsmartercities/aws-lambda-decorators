"""All the classes used as parameters for the decorators."""
from aws_lambda_decorators.decoders import decode
from aws_lambda_decorators.validators import Mandatory
from aws_lambda_decorators.utils import is_type_in_list, is_valid_variable_name

PATH_DIVIDER = '/'
ANNOTATIONS_START = '['
ANNOTATIONS_END = ']'


class ExceptionHandler:
    """Class mapping a friendly error message to a given Exception."""

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


class BaseParameter:  # noqa: pylint - too-few-public-methods
    """Parent class of all parameter classes."""
    def __init__(self, var_name):
        """
            Set the private variables of the BaseParameter object.

            Args:
                var_name (str): The name of the variable where to store the extracted parameter.
        """
        self._name = var_name

    def get_var_name(self):
        """Gets the name of the variable that represents the parameter."""
        if self._name and not is_valid_variable_name(self._name):
            raise SyntaxError(self._name)
        return self._name


class SSMParameter(BaseParameter):
    """Class used for defining the key and, optionally, the variable name for ssm parameter extraction."""

    def __init__(self, ssm_name, var_name=None):
        """
        Set the private variables of the SSMParameter object.

        Args:
            ssm_name (str): Key of the variable in the AWS parameter store
            var_name (str): Optional, the name of variable to store the extracted value to. Defaults to ssm_name.
        """
        self._ssm_name = ssm_name
        BaseParameter.__init__(self, var_name if var_name else ssm_name)

    def get_ssm_name(self):
        """Getter for the ssm_name parameter."""
        return self._ssm_name


class ValidatedParameter:
    """Class used to encapsulate the validation methods parameter data."""

    def __init__(self, func_param_name=None, validators=None):
        """
        Sets the private variables of the ValidatedParameter object.

        Args:
            func_param_name (str): the name for the dictionary in the function signature
                def fun(event, context). To extract from context func_param_name has to be 'context'
            validators (list): A list of validators the value must conform to (e.g. Mandatory(),
                RegexValidator(my_regex), ...)
        """
        self._func_param_name = func_param_name
        self._validators = validators

    @property
    def func_param_name(self):
        """Getter for the func_param_name parameter."""
        return self._func_param_name

    @func_param_name.setter
    def func_param_name(self, value):
        """Setter for the func_param_name parameter."""
        self._func_param_name = value

    def validate(self, value):
        """Check if the given value adheres to the given validation rules."""
        if not self._validators:
            return True
        for validator in self._validators:
            if not validator.validate(value):
                return False
        return True


class Parameter(ValidatedParameter, BaseParameter):
    """Class used to encapsulate the extract methods parameter data."""

    def __init__(self, path='', func_param_name=None, validators=None, var_name=None, default=None):  # noqa: pylint - too-many-arguments
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
            func_param_name (str): the name for the dictionary in the function signature
                def fun(event, context). To extract from context func_param_name has to be 'context'
            validators (list): A list of validators the value must conform to (e.g. Mandatory(),
                RegexValidator(my_regex), ...)
            var_name (str): Optional, the name of the variable we want to assign the extracted value to. The default
                value is the last element of the path (e.g. 'c' in the case above)
            default (any): Optional, a default value if the value is missing and not mandatory.
                The default value is None
        """
        self._path = path
        self._default = default
        ValidatedParameter.__init__(self, func_param_name, validators)
        BaseParameter.__init__(self, var_name)

    @property
    def path(self):
        """Getter for the path parameter."""
        return self._path

    @property
    def default(self):
        """Getter for the default parameter."""
        return self._default

    def extract_value(self, dict_value):
        """
        Calculate and decode the value of the variable in the given path.

        Used by the extract_validated_value.

        Args:
            dict_value (dict): dictionary to be parsed.
        """
        for path_key in filter(lambda item: item != '', self.path.split(PATH_DIVIDER)):
            real_key, annotation = Parameter.get_annotations_from_key(path_key)
            if real_key in dict_value:
                dict_value = decode(annotation, dict_value[real_key])
            else:
                dict_value = self.default
                break

        if not self._name:
            self._name = real_key

        return dict_value

    def extract_validated_value(self, dict_value):
        """
        Extract and validate the extracted value

        Used by the decorators.

        Args:
            dict_value (dict): dictionary to be parsed.

        Raises:
            KeyError: if the parameter does not validate.
        """
        val = self.extract_value(dict_value)
        real_key = self.path.split(PATH_DIVIDER)[-1]

        if (val == self.default and self._validators and is_type_in_list(Mandatory, self._validators)) \
                or not self.validate(val):
            raise KeyError(real_key)

        return val

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
