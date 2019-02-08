import unittest
from unittest.mock import patch, MagicMock, call
from examples.examples import extract_example, extract_to_kwargs_example, extract_mandatory_param_example, \
    extract_from_json_example, extract_from_event_example, extract_from_context_example, extract_from_ssm_example, \
    validate_example, log_example, handle_exceptions_example, response_body_as_json_example


class ExamplesTests(unittest.TestCase):

    def test_extract_example(self):
        #  Given these two dictionaries:
        a_dict = {
            'parent': {
                'my_param': 'Hello!'
            },
            'other': 'other value'
        }
        b_dict = {
            'parent': {
                'child': {
                    'id': '123'
                }
            }
        }

        # calling the decorated extract_example:
        response = extract_example(a_dict, b_dict)

        # will return the values of the extracted parameters
        self.assertEqual(('Hello!', 'I am missing', None, '123'), response)

    def test_extract_to_kwargs_example(self):
        # Given this dictionary:
        dictionary = {
            'parent': {
                'my_param': 'Hello!'
            },
            'other': 'other value'
        }
        # we can extract my_param
        response = extract_to_kwargs_example(dictionary)

        # and get the value from kwargs
        self.assertEqual('Hello!', response)

    def test_extract_missing_mandatory_example(self):
        # Given this dictionary:
        dictionary = {
            'parent': {
                'my_param': 'Hello!'
            },
            'other': 'other value'
        }
        # we can try to extract a missing mandatory parameter
        response = extract_mandatory_param_example(dictionary)

        # but we will get an error response as it is missing and it was mandatory
        self.assertEqual({'statusCode': 400, 'body': 'Error extracting parameters'}, response)

    def test_extract_not_missing_mandatory_example(self):
        # Given this dictionary:
        dictionary = {
            'parent': {
                'mandatory_param': 'Hello!'
            }
        }

        # we can try to extract a mandatory parameter
        response = extract_mandatory_param_example(dictionary)

        # we will get the coded lambda response as the parameter is not missing
        self.assertEqual('Here!', response)

    def test_extract_from_json_example(self):
        # Given this dictionary:
        dictionary = {
            'parent': '{"my_param": "Hello!" }',
            'other': 'other value'
        }

        # we can extract from a json string by adding the [json] annotation to parent
        response = extract_from_json_example(dictionary)

        # and we will get the value of the 'my_param' parameter inside the 'parent' json
        self.assertEqual('Hello!', response)

    def test_extract_from_event_example(self):
        # Given this API Gateway event:
        event = {
            'body': '{"my_param": "Hello!"}',
            'headers': {
                'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9l'
                                 'IiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
            }
        }

        # we can extract 'my_param' from event, and 'sub' from Authorization JWT, using the extract_from_event decorator
        response = extract_from_event_example(event, None)

        # and return both values in the lambda response
        self.assertEqual(('Hello!', '1234567890'), response)

    def test_extract_from_context_example(self):
        # Given this context:
        context = {
            'parent': {
                'my_param': 'Hello!'
            }
        }

        # we can extract 'my_param' from context using the 'extract_from_context' decorator
        response = extract_from_context_example(None, context)

        # and return the value in the lambda response
        self.assertEqual('Hello!', response)

    @patch("boto3.client")
    def test_extract_from_ssm_example(self, mock_boto_client):
        # Mocking the extraction of an SSM parameter from AWS SSM:
        mock_ssm = MagicMock()
        mock_ssm.get_parameters.return_value = {
            "Parameters": [
                {
                    "Value": "test1"
                },
                {
                    "Value": "test2"
                }
            ]
        }
        mock_boto_client.return_value = mock_ssm

        # we can extract the value of that parameter
        response = extract_from_ssm_example(None)

        # and return the mocked SSM parameters from the lambda
        self.assertEqual((None, 'test1', 'test2'), response)

    def test_validate_example(self):
        # We can validate non-dictionary parameters too, using the 'validate' decorator
        response = validate_example('Hello!', '123456')

        # in this case the parameters are valid and are returned by the function
        self.assertEqual(('Hello!', '123456'), response)

    def test_validate_raises_exception_example(self):
        # We can validate non-dictionary parameters too, using the 'validate' decorator
        response = validate_example('Hello!', 'ABCD')

        # in this case at least one parameter is not valid and a 400 error is returned to the caller.
        self.assertEqual({'statusCode': 400, 'body': 'Error validating parameters'}, response)

    @staticmethod
    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_log_example(mock_logger):
        # We can use the 'log' decorator to log the parameters passed to a lambda and/or the response from the lambda.
        log_example('Hello!')  # logs 'Hello!' and 'Done!'

        mock_logger.info.assert_has_calls([
            call('Parameters: %s', ('Hello!',)),
            call('Response: %s', 'Done!')
        ])

    def test_handle_exceptions_example(self):
        self.assertEqual({'body': 'Your message when a client error happens.', 'statusCode': 400},
                         handle_exceptions_example())

    def test_response_as_json_example(self):
        # We can automatically json dump a body dictionary:
        response = response_body_as_json_example()['body']

        # the response body is a string
        self.assertEqual('{"param": "hello!"}', response['body'])
