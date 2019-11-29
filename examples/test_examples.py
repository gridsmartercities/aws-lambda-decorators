import unittest
from unittest.mock import patch, MagicMock, call
from botocore.exceptions import ClientError
from examples.examples import (extract_example, extract_to_kwargs_example, extract_mandatory_param_example,
                               extract_from_json_example, extract_from_event_example, extract_from_context_example,
                               extract_from_ssm_example, validate_example, log_example, handle_exceptions_example,
                               response_body_as_json_example, extract_from_list_example, handle_all_exceptions_example,
                               cors_example, extract_multiple_param_example,
                               extract_minimum_param_with_custom_error_example, extract_dictionary_example,
                               extract_type_param, extract_enum_param, extract_non_empty_param, extract_date_param,
                               extract_with_transform_example, extract_with_custom_transform_example,
                               extract_currency_param)


# pylint:disable=too-many-public-methods
class ExamplesTests(unittest.TestCase):

    def test_extract_example(self):
        #  Given these two dictionaries:
        a_dict = {
            "parent": {
                "my_param": "Hello!"
            },
            "other": "other value"
        }
        b_dict = {
            "parent": {
                "child": {
                    "id": "123"
                }
            }
        }

        # calling the decorated extract_example:
        response = extract_example(a_dict, b_dict)

        # will return the values of the extracted parameters.
        self.assertEqual(("Hello!", "I am missing", None, "123"), response)

    def test_extract_to_kwargs_example(self):
        # Given this dictionary:
        dictionary = {
            "parent": {
                "my_param": "Hello!"
            },
            "other": "other value"
        }
        # we can extract "my_param".
        response = extract_to_kwargs_example(dictionary)

        # and get the value from kwargs.
        self.assertEqual("Hello!", response)

    def test_extract_missing_mandatory_example(self):
        # Given this dictionary:
        dictionary = {
            "parent": {
                "my_param": "Hello!"
            },
            "other": "other value"
        }
        # we can try to extract a missing mandatory parameter.
        response = extract_mandatory_param_example(dictionary)

        # but we will get an error response as it is missing and it was mandatory.
        self.assertEqual(
            {"statusCode": 400, "body": "{\"message\": [{\"mandatory_param\": [\"Missing mandatory value\"]}]}"},
            response)

    def test_extract_multiple_param_example(self):
        # Given this dictionary:
        dictionary = {
            "parent": {
                "my_param": "Hello!",
                "an_int": 20
            },
            "other": "other value"
        }
        # we can try to extract a missing mandatory parameter.
        response = extract_multiple_param_example(dictionary)

        # but we will get an error response as it is missing and it was mandatory.
        self.assertEqual({"statusCode": 400,
                          "body": "{\"message\": [{\"mandatory_param\": [\"Missing mandatory value\"]}, "
                                  "{\"another_mandatory_param\": [\"Missing mandatory value\"]}, "
                                  "{\"an_int\": [\"'20' is greater than maximum value '10'\"]}]}"}, response)

    def test_extract_not_missing_mandatory_example(self):
        # Given this dictionary:
        dictionary = {
            "parent": {
                "mandatory_param": "Hello!"
            }
        }

        # we can try to extract a mandatory parameter.
        response = extract_mandatory_param_example(dictionary)

        # we will get the coded lambda response as the parameter is not missing.
        self.assertEqual("Here!", response)

    def test_extract_from_json_example(self):
        # Given this dictionary:
        dictionary = {
            "parent": "{\"my_param\": \"Hello!\"}",
            "other": "other value"
        }

        # we can extract from a json string by adding the [json] annotation to parent.
        response = extract_from_json_example(dictionary)

        # and we will get the value of the "my_param" parameter inside the "parent" json.
        self.assertEqual("Hello!", response)

    def test_extract_from_event_example(self):
        # Given this API Gateway event:
        event = {
            "body": "{\"my_param\": \"Hello!\"}",
            "headers": {
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9l"
                                 "IiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            }
        }

        # we can extract "my_param" from event, and "sub" from Authorization JWT
        # using the "extract_from_event" decorator.
        response = extract_from_event_example(event, None)

        # and return both values in the lambda response.
        self.assertEqual(("Hello!", "1234567890"), response)

    def test_extract_from_context_example(self):
        # Given this context:
        context = {
            "parent": {
                "my_param": "Hello!"
            }
        }

        # we can extract "my_param" from context using the "extract_from_context" decorator.
        response = extract_from_context_example(None, context)

        # and return the value in the lambda response.
        self.assertEqual("Hello!", response)

    @patch("boto3.client")
    def test_extract_from_ssm_example(self, mock_boto_client):
        # Mocking the extraction of an SSM parameter from AWS SSM:
        mock_ssm = MagicMock()
        mock_ssm.get_parameters.return_value = {
            "Parameters": [
                {
                    "Value": "test1",
                    "Name": "one_key"
                },
                {
                    "Value": "test2",
                    "Name": "another_key"
                }
            ]
        }
        mock_boto_client.return_value = mock_ssm

        # we can extract the value of that parameter.
        response = extract_from_ssm_example(None)

        # and return the mocked SSM parameters from the lambda.
        self.assertEqual((None, "test1", "test2"), response)

    def test_validate_example(self):
        # We can validate non-dictionary parameters too, using the "validate" decorator.
        response = validate_example("Hello!", "123456", {"a": {"b": "c"}})

        # in this case the parameters are valid and are returned by the function.
        self.assertEqual(("Hello!", "123456", {"a": {"b": "c"}}), response)

    def test_validate_raises_exception_example(self):
        # We can validate non-dictionary parameters too, using the "validate" decorator.
        response = validate_example("Hello!", "123456", {"a": 123456})

        # in this case at least one parameter is not valid and a 400 error is returned to the caller.
        self.assertEqual({
            "statusCode": 400,
            "body": "{\"message\": [{\"param_with_schema\": [\"'{'a': 123456}' does not validate against schema"
                    " 'Schema({'a': Or(<class 'str'>, <class 'dict'>)})'\"]}]}"}, response)

    @staticmethod
    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_log_example(mock_logger):
        # We can use the "log" decorator to log the parameters passed to a lambda and/or the response from the lambda.
        log_example("Hello!")  # logs "Hello!" and "Done!"

        # and check the log messages were produced.
        mock_logger.info.assert_has_calls([
            call("Parameters: %s", ("Hello!",)),
            call("Response: %s", "Done!")
        ])

    @patch("boto3.resource")
    def test_handle_exceptions_example(self, mock_dynamo):
        # Mocking the dynamo query to return a ClientError.
        mock_table = MagicMock()
        client_error = ClientError({}, "")
        mock_table.query.side_effect = client_error

        mock_dynamo.return_value.Table.return_value = mock_table

        # we can automatically handle the ClientError, using the "exception_handler" decorator.
        response = handle_exceptions_example()  # noqa: pylint - assignment-from-no-return

        # and return the error supplied to the caller.
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["body"], "{\"message\": \"Your message when a client error happens.\"}")

    def test_response_as_json_example(self):
        # We can automatically json dump a body dictionary:
        response = response_body_as_json_example()

        # the response body is a string.
        self.assertEqual("{\"param\": \"hello!\"}", response["body"])

    def test_extract_from_list_example(self):
        # Given this dictionary:
        dictionary = {
            "parent": [
                {"my_param": "Hello!"},
                {"my_param": "Bye!"}
            ],
            "other": "other value"
        }

        # we can extract from a json string by adding the [json] annotation to parent.
        response = extract_from_list_example(dictionary)

        # and we will get the value of the "my_param" parameter inside the "parent" correct item.
        self.assertEqual("Bye!", response)

    def test_handle_all_exceptions_example(self):
        # we can automatically handle any exceptions, using the "handle_all_exceptions" decorator.
        response = handle_all_exceptions_example()  # noqa: pylint - assignment-from-no-return

        # and return the error to the caller.
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["body"], "{\"message\": \"list index out of range\"}")

    def test_cors(self):
        # you can automatically add CORS headers to any function, using the "cors" decorator.
        response = cors_example()

        # the response has been decorated with the access-control cors headers.
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["access-control-allow-origin"], "*")
        self.assertEqual(response["headers"]["access-control-allow-methods"], "POST")
        self.assertEqual(response["headers"]["access-control-allow-headers"], "Content-Type")
        self.assertEqual(response["headers"]["access-control-max-age"], 86400)

    def test_extract_minimum_param_with_custom_error_example(self):
        # You can add custom error messages to all validators, and incorporate to those error messages
        # the validated value and the validation condition.
        response = extract_minimum_param_with_custom_error_example({"parent": {"an_int": 10}})

        # The error response contains the custom error message, with the correct value to validate
        # and condition to check.
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["body"], "{\"message\": [{\"an_int\": [\"Bad value 10: should be at least 100\"]}]}")

    def test_extract_dictionary_example(self):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "my_param_1": "Hello!",
                "my_param_2": "Bye!"
            }
        }

        # calling the decorated extract_dictionary_example:
        response = extract_dictionary_example(a_dictionary)

        # will return the extracted values in a dictionary.
        self.assertEqual({"my_param_1": "Hello!", "my_param_2": "Bye!"}, response)

    def test_extract_type_param(self):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "a_bool": True
            }
        }

        # calling the decorated extract_dictionary_example:
        response = extract_type_param(a_dictionary)

        # will return the extracted values in a dictionary.
        self.assertEqual(True, response)

    def test_extract_enum_param(self):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "an_enum": "Bye"
            }
        }

        # calling the decorated extract_dictionary_example:
        response = extract_enum_param(a_dictionary)

        # will return the extracted values in a dictionary.
        self.assertEqual("Bye", response)

    def test_extract_non_empty_param(self):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "non_empty": ["first value"]
            }
        }

        # calling the decorated extract_dictionary_example:
        response = extract_non_empty_param(a_dictionary)

        # will return the extracted values in a dictionary.
        self.assertEqual(["first value"], response)

    def test_extract_date_param(self):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "date_example": "2001-01-01 00:00:00"
            }
        }

        # calling the decorated extract_dictionary_example:
        response = extract_date_param(a_dictionary)

        # will return the extracted values in a dictionary.
        self.assertEqual("2001-01-01 00:00:00", response)

    def test_extract_currency_param(self):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "currency_example": "GBP"
            }
        }

        # calling the decorated extract_dictionary_example:
        response = extract_currency_param(a_dictionary)

        # will return the extracted values in a dictionary.
        self.assertEqual("GBP", response)

    def test_extract_with_transform(self):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "my_param": "2"
            }
        }

        # calling the decorated extract_with_transform_example:
        response = extract_with_transform_example(a_dictionary)

        # will return the integer value 2 ("2" transform to an int)
        self.assertEqual(2, response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_with_custom_transform(self, mock_logger):
        # Given this dictionary:
        a_dictionary = {
            "params": {
                "my_param": "abc"
            }
        }

        # calling the decorated extract_with_custom_transform_example:
        response = extract_with_custom_transform_example(a_dictionary)

        # The error response contains a generic error
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["body"], "{\"message\": \"Error extracting parameters\"}")

        # and the logs will contain the "My custom error message" message
        mock_logger.error.assert_called_once_with("%s: %s in argument %s for path %s",
                                                  "Exception",
                                                  "My custom error message",
                                                  "a_dictionary",
                                                  "/params/my_param")
