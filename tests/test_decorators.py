# pylint:disable=too-many-lines
from http import HTTPStatus
import json
from json import JSONDecodeError
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from botocore.exceptions import ClientError
from schema import Schema, And, Optional

from aws_lambda_decorators.classes import ExceptionHandler, Parameter, SSMParameter, ValidatedParameter
from aws_lambda_decorators.decorators import extract, extract_from_event, extract_from_context, handle_exceptions, \
    log, response_body_as_json, extract_from_ssm, validate, handle_all_exceptions, cors
from aws_lambda_decorators.validators import Mandatory, RegexValidator, SchemaValidator, Minimum, Maximum, MaxLength, \
    MinLength, Type, EnumValidator, NonEmpty, DateValidator

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
        response = param.extract_value(dictionary)
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
        response = param.extract_value(dictionary)
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
            param.extract_value(dictionary)

        self.assertTrue("Expecting property name enclosed in double quotes" in context.exception.msg)

    def test_can_get_value_from_dict_with_json_by_path(self):
        path = "/a/b[json]/c"
        dictionary = {
            "a": {
                "b": "{\"c\": \"hello\"}",
                "c": "bye"
            }
        }
        param = Parameter(path, "event")
        response = param.extract_value(dictionary)
        self.assertEqual("hello", response)

    def test_can_get_value_from_dict_with_jwt_by_path(self):
        path = "/a/b[jwt]/sub"
        dictionary = {
            "a": {
                "b": TEST_JWT
            }
        }
        param = Parameter(path, "event")
        response = param.extract_value(dictionary)
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

        @extract([Parameter(path, "event")])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": \"Error extracting parameters\"}", response["body"])

    def test_extract_returns_400_on_missing_mandatory_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path, "event", validators=[Mandatory])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": [{\"c\": [\"Missing mandatory value\"]}]}", response["body"])

    def test_can_add_name_to_parameter(self):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract([Parameter(path, "event", validators=[Mandatory], var_name="custom")])
        def handler(event, context, custom=None):  # noqa
            return custom

        response = handler(dictionary, None)

        self.assertEqual("hello", response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_can_not_add_non_pythonic_var_name_to_parameter(self, mock_logger):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract_from_event([Parameter(path, validators=[Mandatory], var_name="with space")])
        def handler(event, context):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": \"Error extracting parameters\"}", response["body"])

        mock_logger.error.assert_called_once_with(
            "%s: %s in argument %s for path %s",
            "SyntaxError",
            "with space",
            "event",
            "/a/b")

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_can_not_add_pythonic_keyword_as_name_to_parameter(self, mock_logger):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract_from_event([Parameter(path, validators=[Mandatory], var_name="class")])
        def handler(event, context):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": \"Error extracting parameters\"}", response["body"])

        mock_logger.error.assert_called_once_with(
            "%s: %s in argument %s for path %s",
            "SyntaxError",
            "class",
            "event",
            "/a/b")

    def test_extract_does_not_raise_an_error_on_missing_optional_key(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path, "event")])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual({}, response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_returns_400_on_invalid_regex_key(self, mock_logger):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "hello"
                }
            }
        }

        #  Expect a number
        @extract([Parameter(path, "event", [RegexValidator(r"\d+")])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)
        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": [{\"c\": [\"\'hello\' does not conform to regular expression \'\\\\d+\'\"]}]}",
                         response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"c": ["'hello' does not conform to regular expression '\\d+'"]}]
        )

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
        @extract([Parameter(path, "event", [RegexValidator(r"\d+")])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual({}, response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_validate_raises_an_error_on_invalid_variables(self, mock_logger):
        @validate([
            ValidatedParameter(func_param_name="var1", validators=[RegexValidator(r"\d+")]),
            ValidatedParameter(func_param_name="var2", validators=[RegexValidator(r"\d+")])
        ])
        def handler(var1=None, var2=None):  # noqa: pylint - unused-argument
            return {}

        response = handler("2019", "abcd")

        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"var2\": [\"\'abcd\' does not conform to regular expression \'\\\\d+\'\"]}]}",
            response["body"]
        )

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"var2": ["\'abcd\' does not conform to regular expression \'\\d+\'"]}]
        )

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_validate_raises_multiple_errors_on_exit_on_error_false(self, mock_logger):
        @validate([
            ValidatedParameter(func_param_name="var1", validators=[RegexValidator(r"\d+")]),
            ValidatedParameter(func_param_name="var2", validators=[RegexValidator(r"\d+")])
        ], True)
        def handler(var1=None, var2=None):  # noqa: pylint - unused-argument
            return {}

        response = handler("20wq19", "abcd")

        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"var1\": [\"\'20wq19\' does not conform to regular expression \'\\\\d+\'\"]}, "
            "{\"var2\": [\"\'abcd\' does not conform to regular expression \'\\\\d+\'\"]}]}",
            response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [
                {"var1": ["'20wq19' does not conform to regular expression '\\d+'"]},
                {"var2": ["'abcd' does not conform to regular expression '\\d+'"]}
            ]
        )

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_can_not_validate_non_pythonic_var_name(self, mock_logger):
        @validate([
            ValidatedParameter(func_param_name="var 1", validators=[RegexValidator(r"\d+")]),
            ValidatedParameter(func_param_name="var2", validators=[RegexValidator(r"\d+")])
        ], True)
        def handler(var1=None, var2=None):  # noqa: pylint - unused-argument
            return {}

        response = handler("20wq19", "abcd")

        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": \"Error extracting parameters\"}",
            response["body"])

        mock_logger.error.assert_called_once_with("%s: %s in argument %s", "KeyError", "'var 1'", "var 1")

    def test_validate_does_not_raise_an_error_on_valid_variables(self):
        @validate([
            ValidatedParameter(func_param_name="var1", validators=[RegexValidator(r"\d+")]),
            ValidatedParameter(func_param_name="var2", validators=[RegexValidator(r"[ab]+")])
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
        self.assertEqual("{\"message\": \"Error extracting parameters\"}", response["body"])

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_exception_handler_raises_exception(self, mock_logger):

        @handle_exceptions(handlers=[ExceptionHandler(KeyError, "msg")])
        def handler():
            raise KeyError("blank")

        response = handler()  # noqa

        self.assertEqual(400, response["statusCode"])
        self.assertTrue("msg" in response["body"])

        mock_logger.error.assert_called_once_with("%s: %s", "msg", "'blank'")

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_exception_handler_raises_exception_without_friendly_message(self, mock_logger):

        @handle_exceptions(handlers=[ExceptionHandler(KeyError)])
        def handler():
            raise KeyError("blank")

        response = handler()  # noqa

        self.assertEqual(400, response["statusCode"])
        self.assertTrue("blank" in response["body"])

        mock_logger.error.assert_called_once_with("'blank'")

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_exception_handler_raises_exception_with_status_code(self, mock_logger):

        @handle_exceptions(handlers=[ExceptionHandler(KeyError, "error", 500)])
        def handler():
            raise KeyError("blank")

        response = handler()  # noqa

        self.assertEqual(500, response["statusCode"])
        self.assertEqual("""{"message": "error"}""", response["body"])

        mock_logger.error.assert_called_once_with("%s: %s", "error", "'blank'")

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_log_decorator_can_log_params(self, mock_logger):  # noqa: pylint - no-self-use

        @log(True, False)
        def handler(event, context, an_other):  # noqa
            return {}

        handler("first", "{\"tests\": \"a\"}", "another")

        mock_logger.info.assert_called_once_with("Parameters: %s", ("first", "{\"tests\": \"a\"}", "another"))

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_log_decorator_can_log_response(self, mock_logger):  # noqa: pylint - no-self-use

        @log(False, True)
        def handler():
            return {"statusCode": 201}

        handler()

        mock_logger.info.assert_called_once_with("Response: %s", {"statusCode": 201})

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
            return {"statusCode": 200, "body": {"a": "b"}}

        response = handler()

        self.assertEqual(response, {"statusCode": 200, "body": "{\"a\": \"b\"}"})

    def test_body_dump_raises_exception_on_invalid_json(self):

        @response_body_as_json
        def handler():
            return {"statusCode": 200, "body": {"a"}}

        response = handler()

        self.assertEqual(
            response,
            {"statusCode": 500, "body": "{\"message\": \"Response body is not JSON serializable\"}"})

    def test_response_as_json_invalid_application_does_nothing(self):

        @response_body_as_json
        def handler():
            return {"statusCode": 200}

        response = handler()

        self.assertEqual(response, {"statusCode": 200})

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_handle_all_exceptions(self, mock_logger):

        @handle_all_exceptions()
        def handler():
            raise KeyError("blank")

        response = handler()  # noqa

        self.assertEqual(400, response["statusCode"])
        self.assertTrue("blank" in response["body"])

        mock_logger.error.assert_called_once_with("'blank'")

    def test_cors_no_headers_in_response(self):

        @cors(allow_origin="*", allow_methods="POST", allow_headers="Content-Type", max_age=12)
        def handler():
            return {}

        response = handler()

        self.assertEqual(response["headers"]["access-control-allow-headers"], "Content-Type")
        self.assertEqual(response["headers"]["access-control-allow-methods"], "POST")
        self.assertEqual(response["headers"]["access-control-allow-origin"], "*")
        self.assertEqual(response["headers"]["access-control-max-age"], 12)

    def test_cors_adds_correct_headers_only(self):

        @cors(allow_origin="*")
        def handler():
            return {}

        response = handler()

        self.assertEqual(response["headers"]["access-control-allow-origin"], "*")
        self.assertTrue("access-control-allow-methods" not in response["headers"])
        self.assertTrue("access-control-allow-headers" not in response["headers"])
        self.assertTrue("access-control-max-age" not in response["headers"])

    def test_cors_with_headers_in_response(self):

        @cors(allow_origin="*", allow_methods="POST", allow_headers="Content-Type", max_age=12)
        def handler():
            return {
                "headers": {
                    "content-type": "application/json",
                    "access-control-allow-origin": "http://example.com"
                }
            }

        response = handler()

        self.assertEqual(response["headers"]["access-control-allow-headers"], "Content-Type")
        self.assertEqual(response["headers"]["access-control-allow-methods"], "POST")
        self.assertEqual(response["headers"]["access-control-allow-origin"], "http://example.com,*")
        self.assertEqual(response["headers"]["access-control-max-age"], 12)

    def test_cors_with_headers_a_none_value_does_not_remove_headers(self):

        @cors(allow_origin=None)
        def handler():
            return {
                "headers": {
                    "access-control-allow-origin": "http://example.com"
                }
            }

        response = handler()

        self.assertEqual(response["headers"]["access-control-allow-origin"], "http://example.com")
        self.assertTrue("access-control-allow-methods" not in response["headers"])
        self.assertTrue("access-control-allow-headers" not in response["headers"])
        self.assertTrue("access-control-max-age" not in response["headers"])

    def test_cors_with_headers_an_empty_value_does_not_remove_headers(self):

        @cors(allow_origin="")
        def handler():
            return {
                "headers": {
                    "access-control-allow-origin": "http://example.com"
                }
            }

        response = handler()

        self.assertEqual(response["headers"]["access-control-allow-origin"], "http://example.com")

    def test_cors_with_uppercase_headers_in_response(self):

        @cors(allow_origin="*", allow_methods="POST", allow_headers="Content-Type", max_age=12)
        def handler():
            return {
                "Headers": {
                    "content-type": "application/json",
                    "Access-Control-Allow-Origin": "http://example.com"
                }
            }

        response = handler()

        self.assertEqual(response["Headers"]["access-control-allow-headers"], "Content-Type")
        self.assertEqual(response["Headers"]["access-control-allow-methods"], "POST")
        self.assertEqual(response["Headers"]["Access-Control-Allow-Origin"], "http://example.com,*")
        self.assertEqual(response["Headers"]["access-control-max-age"], 12)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_cors_invalid_max_age_logs_error(self, mock_logger):

        @cors(max_age="12")
        def handler():
            return {}

        response = handler()

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(response["body"], "{\"message\": \"Invalid value type in CORS header\"}")

        mock_logger.error.assert_called_once_with("Cannot set %s header to a non %s value",
                                                  "access-control-max-age",
                                                  int)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_cors_cannot_decorate_non_dict(self, mock_logger):

        @cors(allow_origin="*")
        def handler():
            return "I am a string"

        response = handler()

        self.assertEqual(response["statusCode"], 500)  # noqa: pylint-invalid-sequence-index
        self.assertEqual(response["body"], "{\"message\": \"Invalid response type for CORS headers\"}")  # noqa: pylint-invalid-sequence-index

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

        @extract([Parameter(path, "event", validators=[SchemaValidator(schema)])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"a\": [\"\'{\'b\': {\'c\': 3}}\' "
            "does not validate against schema "
            "\'Schema({\'b\': And(<class \'dict\'>, {\'c\': <class \'str\'>})})\'\"]}]}",
            response["body"])

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

        @extract([Parameter(path, "event", validators=[SchemaValidator(schema)])])
        def handler(event, context, a=None):  # noqa
            return a

        response = handler(dictionary, None)

        expected = {
            "b": {
                "c": "d"
            }
        }
        self.assertEqual(expected, response)

    def test_extract_schema_when_property_is_none(self):
        path = "/a/b"
        dictionary = {
            "a": {}
        }

        schema = Schema(
            {
                "b": And(dict, {
                    "c": str
                }),
                Optional("j"): str
            }
        )

        @extract([Parameter(path, "event", validators=[SchemaValidator(schema)])])
        def handler(event, context, b=None):  # noqa
            return b

        response = handler(dictionary, None)

        self.assertEqual(None, response)

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
        self.assertEqual(
            "{\"message\": [{\"value\": [\"\'5\' is less than minimum value \'10.0\'\"]}]}",
            response["body"])

    def test_error_extracting_non_numeric_parameter_with_minimum(self):
        event = {
            "value": "20"
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            "{\"message\": [{\"value\": [\"\'20\' is less than minimum value \'10.0\'\"]}]}", response["body"])

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

        @extract([Parameter("/value", "event", validators=[Minimum(10.0), Mandatory])])
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
            "{\"message\": [{\"value\": [\"\'105\' is greater than maximum value \'100.0\'\"]}]}", response["body"])

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
            "{\"message\": [{\"value\": [\"\'20\' is greater than maximum value \'100.0\'\"]}]}", response["body"])

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

        @extract([Parameter("/value", "event", validators=[Maximum(100.0), Mandatory])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_mandatory_parameter_with_range(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[Minimum(10.0), Maximum(100.0), Mandatory])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_parameter_with_maximum_length(self):
        event = {
            "value": "correct"
        }

        @extract([Parameter("/value", "event", validators=[MaxLength(20)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_error_extracting_parameter_with_max_length(self):
        event = {
            "value": "too long"
        }

        @extract([Parameter("/value", "event", validators=[MaxLength(5)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            "{\"message\": [{\"value\": [\"\'too long\' is longer than maximum length \'5\'\"]}]}",
            response["body"])

    def test_values_are_stringified_in_max_length_validator(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[MaxLength(5)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_optional_null_parameter_with_max_length(self):
        event = {
        }

        @extract([Parameter("/value", "event", validators=[MaxLength(5)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_mandatory_parameter_with_max_length(self):
        event = {
            "value": "aa"
        }

        @extract([Parameter("/value", "event", validators=[MaxLength(5), Mandatory])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_parameter_with_mainimum_length(self):
        event = {
            "value": "correct"
        }

        @extract([Parameter("/value", "event", validators=[MinLength(4)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_error_extracting_parameter_with_min_length(self):
        event = {
            "value": "too short"
        }

        @extract([Parameter("/value", "event", validators=[MinLength(15)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            "{\"message\": [{\"value\": [\"\'too short\' is shorter than minimum length \'15\'\"]}]}",
            response["body"])

    def test_values_are_stringified_in_min_length_validator(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[MinLength(1)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_optional_null_parameter_with_min_length(self):
        event = {
        }

        @extract([Parameter("/value", "event", validators=[MinLength(5)])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_mandatory_parameter_with_min_length(self):
        event = {
            "value": "aa"
        }

        @extract([Parameter("/value", "event", validators=[MaxLength(2), Mandatory])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    def test_extract_mandatory_parameter_with_length_range(self):
        event = {
            "value": "right in the middle"
        }

        @extract([Parameter("/value", "event", validators=[MinLength(10), MaxLength(100), Mandatory])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event)
        self.assertEqual({}, response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_exit_on_error_false_bundles_all_errors(self, mock_logger):
        path_1 = "/a/b/c"
        path_2 = "/a/b/d"
        path_3 = "/a/b/e"
        path_4 = "/a/b/f"
        path_5 = "/a/b/g"
        dictionary = {
            "a": {
                "b": {
                    "e": 23,
                    "f": 15,
                    "g": "a"
                }
            }
        }

        schema = Schema(
            {
                "g": int
            }
        )

        @extract([
            Parameter(path_1, "event", validators=[Mandatory], var_name="c"),
            Parameter(path_2, "event", validators=[Mandatory]),
            Parameter(path_3, "event", validators=[Minimum(30)]),
            Parameter(path_4, "event", validators=[Maximum(10)]),
            Parameter(path_5, "event", validators=[
                RegexValidator(r"[0-9]+"),
                RegexValidator(r"[1][0-9]+"),
                SchemaValidator(schema),
                MinLength(2),
                MaxLength(0)
            ])
        ], True)
        def handler(event, context, c=None, d=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(dictionary, None)
        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"c\": [\"Missing mandatory value\"]}, "
            "{\"d\": [\"Missing mandatory value\"]}, "
            "{\"e\": [\"\'23\' is less than minimum value \'30\'\"]}, "
            "{\"f\": [\"\'15\' is greater than maximum value \'10\'\"]}, "
            "{\"g\": [\"\'a\' does not conform to regular expression \'[0-9]+\'\", "
            "\"\'a\' does not conform to regular expression \'[1][0-9]+\'\", "
            "\"\'a\' does not validate against schema \'Schema({\'g\': <class \'int\'>})\'\", "
            "\"\'a\' is shorter than minimum length \'2\'\", "
            "\"\'a\' is longer than maximum length \'0\'\""
            "]}]}",
            response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [
                {"c": ["Missing mandatory value"]},
                {"d": ["Missing mandatory value"]},
                {"e": ["'23' is less than minimum value '30'"]},
                {"f": ["'15' is greater than maximum value '10'"]},
                {"g": [
                    "'a' does not conform to regular expression '[0-9]+'",
                    "'a' does not conform to regular expression '[1][0-9]+'",
                    "'a' does not validate against schema 'Schema({'g': <class 'int'>})'",
                    "'a' is shorter than minimum length '2'",
                    "'a' is longer than maximum length '0'"
                ]}
            ]
        )

    def test_group_errors_true_returns_ok(self):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract([Parameter(path, "event", validators=[Mandatory])], True)
        def handler(event, context, b=None):  # noqa
            return b

        response = handler(dictionary, None)

        self.assertEqual("hello", response)

    def test_mandatory_parameter_with_default_returns_error_on_empty(self):
        event = {
            "var": ""
        }

        @extract([
            Parameter("/var", "event", validators=[Mandatory], default="hello")
        ])
        def handler(event, context, var=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual("{\"message\": [{\"var\": [\"Missing mandatory value\"]}]}", response["body"])

    def test_group_errors_true_on_extract_from_event_returns_ok(self):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract_from_event([Parameter(path, validators=[Mandatory])], True)
        def handler(event, context, b=None):  # noqa
            return b

        response = handler(dictionary, None)

        self.assertEqual("hello", response)

    def test_group_errors_true_on_extract_from_context_returns_ok(self):
        path = "/a/b"
        dictionary = {
            "a": {
                "b": "hello"
            }
        }

        @extract_from_context([Parameter(path, validators=[Mandatory])], True)
        def handler(event, context, b=None):  # noqa
            return b

        response = handler(None, dictionary)

        self.assertEqual("hello", response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_can_output_custom_error_message_on_validation_failure(self, mock_logger):
        path_1 = "/a/b/c"
        path_2 = "/a/b/d"
        path_3 = "/a/b/e"
        path_4 = "/a/b/f"
        path_5 = "/a/b/g"
        dictionary = {
            "a": {
                "b": {
                    "e": 23,
                    "f": 15,
                    "g": "a"
                }
            }
        }

        schema = Schema(
            {
                "g": int
            }
        )

        @extract([
            Parameter(path_1, "event", validators=[Mandatory("Missing c")], var_name="c"),
            Parameter(path_2, "event", validators=[Mandatory("Missing d")]),
            Parameter(path_3, "event", validators=[Minimum(30, "Bad e value {value}, should be at least {condition}")]),
            Parameter(path_4, "event", validators=[Maximum(10, "Bad f")]),
            Parameter(path_5, "event", validators=[
                RegexValidator(r"[0-9]+", "Bad g regex 1"),
                RegexValidator(r"[1][0-9]+", "Bad g regex 2"),
                SchemaValidator(schema, "Bad g schema"),
                MinLength(2, "Bad g min length"),
                MaxLength(0, "Bad g max length")
            ])
        ], True)
        def handler(event, context, c=None, d=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"c\": [\"Missing c\"]}, "
            "{\"d\": [\"Missing d\"]}, "
            "{\"e\": [\"Bad e value 23, should be at least 30\"]}, "
            "{\"f\": [\"Bad f\"]}, "
            "{\"g\": [\"Bad g regex 1\", "
            "\"Bad g regex 2\", "
            "\"Bad g schema\", "
            "\"Bad g min length\", "
            "\"Bad g max length\""
            "]}]}",
            response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [
                {"c": ["Missing c"]},
                {"d": ["Missing d"]},
                {"e": ["Bad e value 23, should be at least 30"]},
                {"f": ["Bad f"]},
                {"g": [
                    "Bad g regex 1",
                    "Bad g regex 2",
                    "Bad g schema",
                    "Bad g min length",
                    "Bad g max length"
                ]}
            ]
        )

    def test_extract_returns_400_on_missing_mandatory_key_with_regex(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                }
            }
        }

        @extract([Parameter(path, "event", validators=[Mandatory, RegexValidator("[0-9]+")])], group_errors=True)
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": [{\"c\": [\"Missing mandatory value\"]}]}", response["body"])

    def test_extract_nulls_are_returned(self):
        path = "/a/b"
        dictionary = {
            "a": {
            }
        }

        @extract([Parameter(path, "event", default=None)], allow_none_defaults=True)
        def handler(event, context, **kwargs):  # noqa
            return kwargs["b"]

        response = handler(dictionary, None)

        self.assertEqual(None, response)

    def test_extract_nulls_raises_exception_when_extracted_from_kwargs_if_allow_none_defaults_is_false(self):
        path = "/a/b"
        dictionary = {
            "a": {
            }
        }

        @extract([Parameter(path, "event", default=None)], allow_none_defaults=False)
        def handler(event, context, **kwargs):  # noqa
            return kwargs["b"]

        with self.assertRaises(KeyError):
            handler(dictionary, None)

    def test_extract_nulls_preserve_signature_defaults(self):
        path = "/a/b"
        dictionary = {
            "a": {
            }
        }

        @extract([Parameter(path, "event")])
        def handler(event, context, b="Hello"):  # noqa
            return b

        response = handler(dictionary, None)

        self.assertEqual("Hello", response)

    def test_extract_nulls_default_on_decorator_takes_precedence(self):
        path = "/a/b"
        dictionary = {
            "a": {
            }
        }

        @extract([Parameter(path, "event", default="bye")])
        def handler(event, context, b="Hello"):  # noqa
            return b

        response = handler(dictionary, None)

        self.assertEqual("bye", response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_returns_400_on_invalid_bool_type(self, mock_logger):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": 1
                }
            }
        }

        @extract([Parameter(path, "event", [Type(bool)])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)
        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": [{\"c\": [\"\'1\' is not of type \'bool'\"]}]}", response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"c": ["'1' is not of type 'bool'"]}]
        )

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_returns_400_on_invalid_float_type(self, mock_logger):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": 1
                }
            }
        }

        @extract([Parameter(path, "event", [Type(float)])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)
        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": [{\"c\": [\"\'1\' is not of type \'float'\"]}]}", response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"c": ["'1' is not of type 'float'"]}]
        )

    def test_type_validator_returns_true_when_none_is_passed_in(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": None
                }
            }
        }

        @extract([Parameter(path, "event", [Type(float)])])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)
        self.assertEqual(None, response)

    def test_extract_succeeds_with_valid_type_validation(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": 1
                }
            }
        }

        @extract([Parameter(path, "event", [Type(int)])])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)
        self.assertEqual(1, response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_returns_400_on_value_not_in_list(self, mock_logger):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": "Hello"
                }
            }
        }

        @extract([Parameter(path, "event", [EnumValidator("bye", "test", "another")])])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)
        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"c\": [\"\'Hello\' is not in list \'(\'bye\', \'test\', \'another\')'\"]}]}",
            response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"c": ["'Hello' is not in list '('bye', 'test', 'another')'"]}]
        )

    def test_extract_suceeds_with_valid_enum_validation(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": 123
                }
            }
        }

        @extract([Parameter(path, "event", [EnumValidator("Hello", 123)])])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)
        self.assertEqual(123, response)

    def test_enum_validator_returns_true_when_none_is_passed_in(self):
        path = "/a/b/c"
        dictionary = {
            "a": {
                "b": {
                    "c": None
                }
            }
        }

        @extract([Parameter(path, "event", [EnumValidator("Test", "another")])])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)
        self.assertEqual(None, response)

    def test_extract_from_event_missing_parameter_path(self):
        event = {
            "body": "{}"
        }

        @extract_from_event(parameters=[Parameter(path="body[json]/optional/value", default="Hello")])
        def handler(event, context, **kwargs):  # noqa
            return {
                "statusCode": HTTPStatus.OK,
                "body": json.dumps(kwargs)
            }

        expected_body = json.dumps({
            "value": "Hello"
        })

        response = handler(event, None)

        self.assertEqual(HTTPStatus.OK, response["statusCode"])
        self.assertEqual(expected_body, response["body"])

    def test_extract_non_empty_parameter(self):
        event = {
            "value": 20
        }

        @extract([Parameter("/value", "event", validators=[NonEmpty])])
        def handler(event, value=None):  # noqa: pylint - unused-argument
            return value

        response = handler(event)
        self.assertEqual(20, response)

    def test_extract_missing_non_empty_parameter(self):
        event = {
            "a": 20
        }

        @extract([Parameter("/b", "event", validators=[NonEmpty])])
        def handler(event, b=None):  # noqa: pylint - unused-argument
            return b

        response = handler(event)
        self.assertEqual(None, response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_non_empty_parameter_that_is_empty(self, mock_logger):
        event = {
            "a": {}
        }

        @extract([Parameter("/a", "event", validators=[NonEmpty])])
        def handler(event, a=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"a\": [\"Value is empty\"]}]}",
            response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"a": ["Value is empty"]}]
        )

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_non_empty_parameter_that_is_empty_with_custom_message(self, mock_logger):
        event = {
            "a": {}
        }

        @extract([Parameter("/a", "event", validators=[NonEmpty("The value was empty")])])
        def handler(event, a=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual(
            "{\"message\": [{\"a\": [\"The value was empty\"]}]}",
            response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"a": ["The value was empty"]}]
        )

    def test_extract_date_parameter(self):
        event = {
            "a": "2001-01-01 00:00:00"
        }

        @extract([Parameter("/a", "event", validators=[DateValidator("%Y-%m-%d %H:%M:%S")])])
        def handler(event, a=None):  # noqa: pylint - unused-argument
            return a

        response = handler(event)
        self.assertEqual("2001-01-01 00:00:00", response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_date_parameter_fails_on_invalid_date(self, mock_logger):
        event = {
            "a": "2001-01-01 35:00:00"
        }

        @extract([Parameter("/a", "event", validators=[DateValidator("%Y-%m-%d %H:%M:%S")])])
        def handler(event, a=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": [{\"a\": [\"'2001-01-01 35:00:00' is not a '%Y-%m-%d %H:%M:%S' date\"]}]}",
                         response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"a": ["'2001-01-01 35:00:00' is not a '%Y-%m-%d %H:%M:%S' date"]}]
        )

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_date_parameter_fails_with_custom_error(self, mock_logger):
        event = {
            "a": "2001-01-01 35:00:00"
        }

        @extract([Parameter("/a", "event", validators=[DateValidator("%Y-%m-%d %H:%M:%S", "Not a valid date!")])])
        def handler(event, a=None):  # noqa: pylint - unused-argument
            return {}

        response = handler(event, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": [{\"a\": [\"Not a valid date!\"]}]}", response["body"])

        mock_logger.error.assert_called_once_with(
            "Error validating parameters. Errors: %s",
            [{"a": ["Not a valid date!"]}]
        )

    def test_extract_date_parameter_valid_on_empty(self):
        event = {
            "a": None
        }

        @extract([Parameter("/a", "event", validators=[DateValidator("%Y-%m-%d %H:%M:%S")])])
        def handler(event, a=None):  # noqa: pylint - unused-argument
            return a

        response = handler(event)
        self.assertEqual(None, response)


class IsolatedDecoderTests(unittest.TestCase):
    # Tests have been named so they run in a specific order

    ID_PATTERN = "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

    PARAMETERS = [
        Parameter(path="pathParameters/test_id", validators=[Mandatory, RegexValidator(ID_PATTERN)]),
        Parameter(path="body[json]/name", validators=[MaxLength(255)])
    ]

    def test_01_extract_from_event_400(self):
        event = {
            "pathParameters": {}
        }

        @extract_from_event(parameters=self.PARAMETERS, group_errors=True, allow_none_defaults=False)
        def handler(event, context, **kwargs):  # noqa
            return kwargs

        response = handler(event, None)
        self.assertEqual(HTTPStatus.BAD_REQUEST, response["statusCode"])

    def test_02_extract_from_event_200(self):
        test_id = str(uuid4())

        event = {
            "pathParameters": {
                "test_id": test_id
            },
            "body": json.dumps({
                "name": "Gird"
            })
        }

        @extract_from_event(parameters=self.PARAMETERS, group_errors=True, allow_none_defaults=False)
        def handler(event, context, **kwargs):  # noqa
            return {
                "statusCode": HTTPStatus.OK,
                "body": json.dumps(kwargs)
            }

        expected_body = json.dumps({
            "test_id": test_id,
            "name": "Gird"
        })

        response = handler(event, None)

        self.assertEqual(HTTPStatus.OK, response["statusCode"])
        self.assertEqual(expected_body, response["body"])
