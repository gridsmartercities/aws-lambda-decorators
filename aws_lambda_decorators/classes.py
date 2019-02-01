from aws_lambda_decorators.decoders import decode
from aws_lambda_decorators.validators import Mandatory
from aws_lambda_decorators.utils import is_type_in_list, is_valid_variable_name


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
    def __init__(self, path, validators=None, func_param_index=0, name=None):
        self._func_param_index = func_param_index
        self._path = path
        self._validators = validators
        self._name = name

    @property
    def func_param_index(self):
        return self._func_param_index

    @property
    def path(self):
        return self._path

    @func_param_index.setter
    def func_param_index(self, value):
        self._func_param_index = value

    def get_dict_key_value_by_path(self, args):
        dict_value = args[self._func_param_index]

        for path_key in filter(lambda item: item != "", self.path.split("/")):
            real_key, annotation = Parameter.get_annotations_from_key(path_key)
            if real_key in dict_value:
                dict_value = decode(annotation, dict_value[real_key])
            elif self._validators and is_type_in_list(Mandatory, self._validators):
                raise KeyError(real_key)

        val = dict_value.get(real_key, None) if isinstance(dict_value, dict) else dict_value
        if not self.validate(val):
            raise KeyError(real_key)

        return real_key, dict_value

    def get_name(self, key):
        if self._name and not is_valid_variable_name(self._name):
            raise SyntaxError(self._name)
        return self._name if self._name else key

    def validate(self, value):
        if not self._validators:
            return True
        for validator in self._validators:
            if not validator.validate(value):
                return False
        return True

    @staticmethod
    def get_annotations_from_key(key):
        if '[' in key and ']' in key:
            annotation = key[key.find('[') + 1:key.find(']')]
            return key.replace('[{}]'.format(annotation), ''), annotation
        return key, None
