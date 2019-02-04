from aws_lambda_decorators.decoders import decode
from aws_lambda_decorators.validators import Mandatory
from aws_lambda_decorators.utils import is_type_in_list, is_valid_variable_name

PATH_DIVIDER = '/'
ANNOTATIONS_START = '['
ANNOTATIONS_END = ']'


class ExceptionHandler:
    def __init__(self, exception, friendly_message):
        self._exception = exception
        self._friendly_message = friendly_message

    @property
    def friendly_message(self):
        return self._friendly_message

    @property
    def exception(self):
        return self._exception


class Parameter:
    def __init__(self, path, validators=None, func_param_index=0, var_name=None):
        self._func_param_index = func_param_index
        self._path = path
        self._validators = validators
        self._name = var_name

    @property
    def func_param_index(self):
        return self._func_param_index

    @property
    def path(self):
        return self._path

    @func_param_index.setter
    def func_param_index(self, value):
        self._func_param_index = value

    def get_value_by_path(self, args):
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
        if not self._validators:
            return True
        for validator in self._validators:
            if not validator.validate(value):
                return False
        return True

    def get_var_name(self):
        if self._name and not is_valid_variable_name(self._name):
            raise SyntaxError(self._name)
        return self._name

    @staticmethod
    def get_annotations_from_key(key):
        if ANNOTATIONS_START in key and ANNOTATIONS_END in key:
            annotation = key[key.find(ANNOTATIONS_START) + 1:key.find(ANNOTATIONS_END)]
            return key.replace(ANNOTATIONS_START + annotation + ANNOTATIONS_END, ''), annotation
        return key, None


class SSMParameter:
    def __init__(self, ssm_name, var_name=None):
        self._ssm_name = ssm_name
        self._name = var_name if var_name else ssm_name

    def get_ssm_name(self):
        return self._ssm_name

    def get_var_name(self):
        if self._name and not is_valid_variable_name(self._name):
            raise SyntaxError(self._name)
        return self._name
