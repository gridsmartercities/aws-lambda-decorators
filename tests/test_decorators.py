# pylint:disable=no-self-use
import unittest
from unittest.mock import patch, MagicMock
from json import JSONDecodeError
from botocore.exceptions import ClientError
from schema import Schema, And, Optional
from aws_lambda_decorators.classes import ExceptionHandler, Parameter, SSMParameter, ValidatedParameter
from aws_lambda_decorators.decorators import extract, extract_from_event, extract_from_context, handle_exceptions, \
    log, response_body_as_json, extract_from_ssm, validate, handle_all_exceptions, cors
from aws_lambda_decorators.validators import Mandatory, RegexValidator, SchemaValidator, Minimum, Maximum

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


class DecoratorsTests(unittest.TestCase):  # noqa: pylint - too-many-public-methods

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
        response = param.extract_validated_value(dictionary)
        self.assertEqual("hello", response)

    def test_can_get_dict_value_from_dict_by_path(self):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": {
                    "c": "hello"
                }
            }
        }
        param = Parameter(path)
        response = param.extract_validated_value(dictionary)
        self.assertEqual({"c": "hello"}, response)

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
            param.extract_validated_value(dictionary)

        self.assertTrue("Expecting property name enclosed in double quotes" in context.exception.msg)

    def test_can_get_value_from_dict_with_json_by_path(self):
        path = "/a/b[json]/c"
        dictionary = {
            "a": {
                "b": '{ "c": "hello" }',
                "c": "bye"
            }
        }
        param = Parameter(path, 'event')
        response = param.extract_validated_value(dictionary)
        self.assertEqual("hello", response)

    def test_can_get_value_from_dict_with_jwt_by_path(self):
        path = "/a/b[jwt]/sub"
        dictionary = {
            "a": {
                "b": TEST_JWT
            }
        }
        param = Parameter(path, 'event')
        response = param.extract_validated_value(dictionary)
        self.assertEqual("aadd1e0e-5807-4763-b1e8-5823bf631bb6", response)

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

    def test_extract_from_event_calls_function_with_extra_kwargs_bool_true(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": True
                }
            }
        }

        @extract_from_event([Parameter(path)])
        def handler(event, context, c=None):  # noqa
            return c

        self.assertFalse(handler(dictionary, None) is None)
        self.assertEqual(True, handler(dictionary, None))

    def test_extract_from_event_calls_function_with_extra_kwargs_bool_false(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": False
                }
            }
        }

        @extract_from_event([Parameter(path)])
        def handler(event, context, c=None):  # noqa
            return c

        self.assertFalse(handler(dictionary, None) is None)
        self.assertEqual(False, handler(dictionary, None))

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

    def test_extract_returns_400_on_empty_path(self):
        path = None
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path, 'event')])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

    def test_extract_returns_400_on_missing_mandatory_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path, 'event', validators=[Mandatory()])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

    def test_can_add_name_to_parameter(self):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract([Parameter(path, 'event', validators=[Mandatory()], var_name='custom')])
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

        @extract_from_event([Parameter(path, validators=[Mandatory()], var_name='with space')])
        def handler(event, context):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

        mock_logger.error.assert_called_once_with("%s: '%s' in argument %s for path %s",
                                                  'SyntaxError',
                                                  'with space',
                                                  'event',
                                                  '/a/b')

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_can_not_add_pythonic_keyword_as_name_to_parameter(self, mock_logger):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract_from_event([Parameter(path, validators=[Mandatory()], var_name='class')])
        def handler(event, context):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

        mock_logger.error.assert_called_once_with("%s: '%s' in argument %s for path %s",
                                                  'SyntaxError',
                                                  'class',
                                                  'event',
                                                  '/a/b')

    def test_extract_does_not_raise_an_error_on_missing_optional_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path, 'event')])
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
        @extract([Parameter(path, 'event', [RegexValidator(r'\d+')])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)
        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

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
        @extract([Parameter(path, 'event', [RegexValidator(r'\d+')])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual({}, response)

    def test_validate_raises_an_error_on_invalid_variables(self):
        @validate([
            ValidatedParameter(func_param_name="var1", validators=[RegexValidator(r'\d+')]),
            ValidatedParameter(func_param_name="var2", validators=[RegexValidator(r'\d+')])
        ])
        def handler(var1=None, var2=None):  # noqa: pylint - unused-argument
            return {}

        response = handler("2019", "abcd")
        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error validating parameters"}', response["body"])

    def test_validate_does_not_raise_an_error_on_valid_variables(self):
        @validate([
            ValidatedParameter(func_param_name="var1", validators=[RegexValidator(r'\d+')]),
            ValidatedParameter(func_param_name="var2", validators=[RegexValidator(r'[ab]+')])
        ])
        def handler(var1, var2=None):  # noqa: pylint - unused-argument
            return {}

        response = handler("2019", var2="abba")
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
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

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
    def test_exception_handler_raises_exception_without_friendly_message(self, mock_logger):

        @handle_exceptions(handlers=[ExceptionHandler(KeyError)])
        def handler():
            raise KeyError('blank')

        response = handler()  # noqa

        self.assertEqual(400, response["statusCode"])
        self.assertTrue("blank" in response["body"])

        mock_logger.error.assert_called_once_with("'blank'")

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_log_decorator_can_log_params(self, mock_logger):

        @log(True, False)
        def handler(event, context, an_other):  # noqa
            return {}

        handler("first", "{'tests': 'a'}", "another")

        mock_logger.info.assert_called_once_with('Parameters: %s', ("first", "{'tests': 'a'}", "another"))

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_log_decorator_can_log_response(self, mock_logger):

        @log(False, True)
        def handler():
            return {'statusCode': 201}

        handler()

        mock_logger.info.assert_called_once_with('Response: %s', {'statusCode': 201})

    @patch("boto3.client")
    def test_get_valid_ssm_parameter(self, mock_boto_client):
        mock_ssm = MagicMock()
        mock_ssm.get_parameters.return_value = {
            "Parameters": [
                {
                    "Name": "key",
                    "Value": "tests"
                }
            ]
        }
        mock_boto_client.return_value = mock_ssm

        @extract_from_ssm([SSMParameter("key")])
        def handler(key=None):
            return key

        self.assertEqual(handler(), "tests")

    @patch("boto3.client")
    def test_get_valid_ssm_parameter_custom_name(self, mock_boto_client):
        mock_ssm = MagicMock()
        mock_ssm.get_parameters.return_value = {
            "Parameters": [
                {
                    "Name": "key",
                    "Value": "tests"
                }
            ]
        }
        mock_boto_client.return_value = mock_ssm

        @extract_from_ssm([SSMParameter("key", "custom")])
        def handler(custom=None):
            return custom

        self.assertEqual(handler(), "tests")

    @patch("boto3.client")
    def test_get_valid_ssm_parameters(self, mock_boto_client):
        mock_ssm = MagicMock()
        mock_ssm.get_parameters.return_value = {
            "Parameters": [
                {
                    "Name": "key2",
                    "Value": "test2"
                },
                {
                    "Name": "key1",
                    "Value": "test1"
                }
            ]
        }
        mock_boto_client.return_value = mock_ssm

        @extract_from_ssm([SSMParameter("key1", "key1"), SSMParameter("key2", "key2")])
        def handler(key1=None, key2=None):
            return [key1, key2]

        self.assertEqual(handler(), ["test1", "test2"])

    @patch("boto3.client")
    def test_get_ssm_parameter_missing_parameter_raises_client_error(self, mock_boto_client):
        mock_ssm = MagicMock()
        mock_ssm.get_parameters.side_effect = ClientError({}, "")
        mock_boto_client.return_value = mock_ssm

        @extract_from_ssm([SSMParameter("")])
        def handler(key=None):
            return key

        with self.assertRaises(ClientError):
            handler()

    @patch("boto3.client")
    def test_get_ssm_parameter_empty_key_container_raises_key_error(self, mock_boto_client):
        mock_ssm = MagicMock()
        mock_ssm.get_parameters.return_value = {
        }
        mock_boto_client.return_value = mock_ssm

        @extract_from_ssm([SSMParameter("")])
        def handler(key=None):
            return key

        with self.assertRaises(KeyError):
            handler()

    def test_body_gets_dumped_as_json(self):

        @response_body_as_json
        def handler():
            return {'statusCode': 200, 'body': {'a': 'b'}}

        response = handler()

        self.assertEqual(response, {'statusCode': 200, 'body': '{"a": "b"}'})

    def test_body_dump_raises_exception_on_invalid_json(self):

        @response_body_as_json
        def handler():
            return {'statusCode': 200, 'body': {'a'}}

        response = handler()

        self.assertEqual(response, {'statusCode': 500, 'body': '{"message": "Response body is not JSON serializable"}'})

    def test_response_as_json_invalid_application_does_nothing(self):

        @response_body_as_json
        def handler():
            return {'statusCode': 200}

        response = handler()

        self.assertEqual(response, {'statusCode': 200})

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_handle_all_exceptions(self, mock_logger):

        @handle_all_exceptions()
        def handler():
            raise KeyError('blank')

        response = handler()  # noqa

        self.assertEqual(400, response["statusCode"])
        self.assertTrue("blank" in response["body"])

        mock_logger.error.assert_called_once_with("'blank'")

    def test_cors_no_headers_in_response(self):

        @cors(allow_origin='*', allow_methods='POST', allow_headers='Content-Type', max_age=12)
        def handler():
            return {}

        response = handler()

        self.assertEqual(response['headers']['access-control-allow-headers'], 'Content-Type')
        self.assertEqual(response['headers']['access-control-allow-methods'], 'POST')
        self.assertEqual(response['headers']['access-control-allow-origin'], '*')
        self.assertEqual(response['headers']['access-control-max-age'], 12)

    def test_cors_adds_correct_headers_only(self):

        @cors(allow_origin='*')
        def handler():
            return {}

        response = handler()

        self.assertEqual(response['headers']['access-control-allow-origin'], '*')
        self.assertTrue('access-control-allow-methods' not in response['headers'])
        self.assertTrue('access-control-allow-headers' not in response['headers'])
        self.assertTrue('access-control-max-age' not in response['headers'])

    def test_cors_with_headers_in_response(self):

        @cors(allow_origin='*', allow_methods='POST', allow_headers='Content-Type', max_age=12)
        def handler():
            return {
                'headers': {
                    'content-type': 'application/json',
                    'access-control-allow-origin': 'http://example.com'
                }
            }

        response = handler()

        self.assertEqual(response['headers']['access-control-allow-headers'], 'Content-Type')
        self.assertEqual(response['headers']['access-control-allow-methods'], 'POST')
        self.assertEqual(response['headers']['access-control-allow-origin'], 'http://example.com,*')
        self.assertEqual(response['headers']['access-control-max-age'], 12)

    def test_cors_with_headers_a_none_value_does_not_remove_headers(self):

        @cors(allow_origin=None)
        def handler():
            return {
                'headers': {
                    'access-control-allow-origin': 'http://example.com'
                }
            }

        response = handler()

        self.assertEqual(response['headers']['access-control-allow-origin'], 'http://example.com')
        self.assertTrue('access-control-allow-methods' not in response['headers'])
        self.assertTrue('access-control-allow-headers' not in response['headers'])
        self.assertTrue('access-control-max-age' not in response['headers'])

    def test_cors_with_headers_an_empty_value_does_not_remove_headers(self):

        @cors(allow_origin='')
        def handler():
            return {
                'headers': {
                    'access-control-allow-origin': 'http://example.com'
                }
            }

        response = handler()

        self.assertEqual(response['headers']['access-control-allow-origin'], 'http://example.com')

    def test_cors_with_uppercase_headers_in_response(self):

        @cors(allow_origin='*', allow_methods='POST', allow_headers='Content-Type', max_age=12)
        def handler():
            return {
                'Headers': {
                    'content-type': 'application/json',
                    'Access-Control-Allow-Origin': 'http://example.com'
                }
            }

        response = handler()

        self.assertEqual(response['Headers']['access-control-allow-headers'], 'Content-Type')
        self.assertEqual(response['Headers']['access-control-allow-methods'], 'POST')
        self.assertEqual(response['Headers']['Access-Control-Allow-Origin'], 'http://example.com,*')
        self.assertEqual(response['Headers']['access-control-max-age'], 12)

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_cors_invalid_max_age_logs_error(self, mock_logger):

        @cors(max_age='12')
        def handler():
            return {}

        response = handler()

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], 'Invalid value type in CORS header')

        mock_logger.error.assert_called_once_with("Cannot set %s header to a non %s value",
                                                  'access-control-max-age',
                                                  int)

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_cors_cannot_decorate_non_dict(self, mock_logger):

        @cors(allow_origin='*')
        def handler():
            return 'I am a string'

        response = handler()

        self.assertEqual(response['statusCode'], 500)  # noqa: pylint-invalid-sequence-index
        self.assertEqual(response['body'], "Invalid response type for CORS headers")  # noqa: pylint-invalid-sequence-index

        mock_logger.error.assert_called_once_with("Cannot add headers to a non dictionary response")

    def test_extract_returns_400_on_invalid_dictionary_schema(self):
        path = "/a"
        dictionary = {
            "a": {
                "b": {
                    "c": 3
                }
            }
        }

        schema = Schema(
            {
                "b": And(dict, {
                    "c": str
                })
            }
        )

        @extract([Parameter(path, 'event', validators=[SchemaValidator(schema)])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

    def test_extract_valid_dictionary_schema(self):
        path = "/a"
        dictionary = {
            "a": {
                "b": {
                    "c": "d"
                }
            }
        }

        schema = Schema(
            {
                "b": And(dict, {
                    "c": str
                }),
                Optional("j"): str
            }
        )

        @extract([Parameter(path, 'event', validators=[SchemaValidator(schema)])])
        def handler(event, context, a=None):  # noqa
            return a

        response = handler(dictionary, None)

        expected = {
            "b": {
                "c": "d"
            }
        }
        self.assertEqual(expected, response)

    def test_extract_parameter_with_minimum(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_error_extracting_parameter_with_minimum(self):
        event = {
            "value": 5
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

    def test_error_extracting_non_numeric_parameter_with_minimum(self):
        event = {
            "value": "20"
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

    def test_extract_optional_null_parameter_with_minimum(self):
        event = {
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_mandatory_parameter_with_minimum(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0), Mandatory()])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_parameter_with_maximum(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[Maximum(100.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_error_extracting_parameter_with_maximum(self):
        event = {
            "value": 105
        }

        @extract([Parameter("/value", "event", validators=[Maximum(100.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            '{"message": "Error extracting parameters"}', response["body"])

    def test_error_extracting_non_numeric_parameter_with_maximum(self):
        event = {
            "value": "20"
        }

        @extract([Parameter("/value", "event", validators=[Maximum(100.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            '{"message": "Error extracting parameters"}', response["body"])

    def test_extract_optional_null_parameter_with_maximum(self):
        event = {
        }

        @extract([Parameter("/value", "event", validators=[Maximum(10.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_mandatory_parameter_with_maximum(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[Maximum(100.0), Mandatory()])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_mandatory_parameter_with_range(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0), Maximum(100.0), Mandatory()])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)
