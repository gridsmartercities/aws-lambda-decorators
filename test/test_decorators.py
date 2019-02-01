# pylint:disable=no-self-use
import unittest
from unittest.mock import patch
from json import JSONDecodeError
from aws_lambda_decorators.classes import ExceptionHandler, Parameter
from aws_lambda_decorators.decorators import extract, extract_from_event, extract_from_context, handle_exceptions, log
from aws_lambda_decorators.validators import Mandatory, ValidRegex

TEST_JWT = "eyJraWQiOiJEQlwvK0lGMVptekNWOGNmRE1XVUxBRlBwQnVObW5CU2NcL2RoZ3pnTVhcL2NzPSIsImFsZyI6IlJTMjU2In0." \
           "eyJzdWIiOiJhYWRkMWUwZS01ODA3LTQ3NjMtYjFlOC01ODIzYmY2MzFiYjYiLCJhdWQiOiIycjdtMW1mdWFiODg3ZmZvdG9iNWFjcX" \
           "Q2aCIsImNvZ25pdG86Z3JvdXBzIjpbIkRBU0gtQ3VzdG9tZXIiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImV2ZW50X2lkIjoiZDU4" \
           "NzU0ZjUtMTdlMC0xMWU5LTg2NzAtMjVkOTNhNWNiMjAwIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE1NDc0NTkwMDMsIm" \
           "lzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5ldS13ZXN0LTIuYW1hem9uYXdzLmNvbVwvZXUtd2VzdC0yX1B4bEdzMU11SiIsImNv" \
           "Z25pdG86dXNlcm5hbWUiOiJhYWRkMWUwZS01ODA3LTQ3NjMtYjFlOC01ODIzYmY2MzFiYjYiLCJleHAiOjE1NDc0NjI2MDMsImlhdC" \
           "I6MTU0NzQ1OTAwMywiZW1haWwiOiJjdXN0b21lckBleGFtcGxlLmNvbSJ9.CNSDu4a9azT40maHAF9tnQTWbfEeiTZ9PfkR9_RU_VG" \
           "4QTA1y4R0F2zWVpsa3CkVMq4Uv2NWOwG6zXf-7XaWTEjoGOQR07sq54IEWU3WIxgkgtRAI-aR7nIvllMXXR0RE3e5jzn5SmefG1j-O" \
           "NYiD1yYExrKOEMPJVgkdYG6x2cBiucHihVliJQUf9u-ebpu2Cpm_ACvUTUilB6sBL06D3sRobvNLbNNnSjsA66ULNpPTPOVYJxhFbu" \
           "ceQ1EICp0oICw2ncJch78RAFY5TeqiVa-uBybxwd36zJmZkXeJPWAKd32IOIJXNUyDOJtmXtSQW51pZGYTsihjZHz3kNlfg"


class DecoratorsTests(unittest.TestCase):

    def test_can_get_value_from_dict_by_path(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "hello"
                }
            }
        }
        param = Parameter(path)
        response = param.get_dict_key_value_by_path([dictionary])
        self.assertEqual(("c", "hello"), response)

    def test_raises_decode_error_convert_json_string_to_dict(self):
        path = "/a/b[json]/c"
        dictionary = {
            "a": {
                "b": "{ 'c': 'hello' }",
                "c": "bye"
            }
        }
        param = Parameter(path)
        with self.assertRaises(JSONDecodeError) as context:
            param.get_dict_key_value_by_path([dictionary])

        self.assertTrue("Expecting property name enclosed in double quotes" in context.exception.msg)

    def test_can_get_value_from_dict_with_json_by_path(self):
        path = "/a/b[json]/c"
        dictionary = {
            "a": {
                "b": '{ "c": "hello" }',
                "c": "bye"
            }
        }
        param = Parameter(path)
        response = param.get_dict_key_value_by_path([dictionary])
        self.assertEqual(("c", "hello"), response)

    def test_can_get_value_from_dict_with_jwt_by_path(self):
        path = "/a/b[jwt]/sub"
        dictionary = {
            "a": {
                "b": TEST_JWT
            }
        }
        param = Parameter(path)
        response = param.get_dict_key_value_by_path([dictionary])
        self.assertEqual(("sub", "aadd1e0e-5807-4763-b1e8-5823bf631bb6"), response)

    def test_extract_from_event_calls_function_with_extra_kwargs(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "hello"
                }
            }
        }

        @extract_from_event([Parameter(path)])
        def handler(event, context, c=None):  # noqa
            return c

        self.assertEqual(handler(dictionary, None), "hello")

    def test_extract_from_context_calls_function_with_extra_kwargs(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "hello"
                }
            }
        }

        @extract_from_context([Parameter(path)])
        def handler(event, context, c=None):  # noqa
            return c

        self.assertEqual(handler(None, dictionary), "hello")

    def test_extract_returns_400_on_missing_mandatory_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path, [Mandatory()], func_param_index=0)])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('Error extracting parameters', response["body"])

    def test_can_add_name_to_parameter(self):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract([Parameter(path, [Mandatory()], func_param_index=0, name='custom')])
        def handler(event, context, custom=None):  # noqa
            return custom

        response = handler(dictionary, None)

        self.assertEqual("hello", response)

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_can_not_add_non_pythonic_var_name_to_parameter(self, mock_logger):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract_from_event([Parameter(path, validators=[Mandatory()], name='with space')])
        def handler(event, context):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('Error extracting parameters', response["body"])

        mock_logger.error.assert_called_once_with("SyntaxError: 'with space' in index 0 for path /a/b")

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_can_not_add_pythonic_keyword_as_name_to_parameter(self, mock_logger):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract_from_event([Parameter(path, validators=[Mandatory()], name='class')])
        def handler(event, context):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('Error extracting parameters', response["body"])

        mock_logger.error.assert_called_once_with("SyntaxError: 'class' in index 0 for path /a/b")

    def test_extract_does_not_raise_an_error_on_missing_optional_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path)])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual({}, response)

    def test_extract_returns_400_on_invalid_regex_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "hello"
                }
            }
        }

        #  Expect a number
        @extract([Parameter(path, [ValidRegex(r'\d+')])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)
        self.assertEqual(400, response["statusCode"])
        self.assertEqual("Error extracting parameters", response["body"])

    def test_extract_does_not_raise_an_error_on_valid_regex_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "2019"
                }
            }
        }

        #  Expect a number
        @extract([Parameter(path, [ValidRegex(r'\d+')])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual({}, response)

    def test_extract_returns_400_on_type_error(self):
        path = "/a/b[json]/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "hello"
                }
            }
        }

        @extract([Parameter(path)])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('Error extracting parameters', response["body"])

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_exception_handler_raises_exception(self, mock_logger):

        @handle_exceptions(handlers=[ExceptionHandler(KeyError, "msg")])
        def handler():
            raise KeyError('blank')

        response = handler()  # noqa

        self.assertEqual(400, response["statusCode"])
        self.assertTrue("msg" in response["body"])

        mock_logger.error.assert_called_once_with("msg: 'blank'")

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_log_decorator_can_log_params(self, mock_logger):

        @log(True, False)
        def handler(event, context, an_other):  # noqa
            return {}

        handler("first", "{'test': 'a'}", "another")

        mock_logger.info.assert_called_once_with("first", "{'test': 'a'}", "another")

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_log_decorator_can_log_response(self, mock_logger):

        @log(False, True)
        def handler():
            return {'responseCode': 201}

        handler()

        mock_logger.info.assert_called_once_with({'responseCode': 201})
