import unittest
from unittest.mock import patch, MagicMock, call
from botocore.exceptions import ClientError
from examples.examples import extract_example, extract_to_kwargs_example, extract_missing_mandatory_param_example, \
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

        self.assertEqual(('Hello!', 'I am missing', None, '123'), extract_example(a_dict, b_dict))

    def test_extract_to_kwargs_example(self):
        dictionary = {
            'parent': {
                'my_param': 'Hello!'
            },
            'other': 'other value'
        }

        self.assertEqual('Hello!', extract_to_kwargs_example(dictionary))

    def test_extract_missing_mandatory_example(self):
        response = extract_missing_mandatory_param_example({'parent': {'my_param': 'Hello!'}, 'other': 'other value'})

        self.assertEqual({'statusCode': 400, 'body': 'Error extracting parameters'}, response)

    def test_extract_not_missing_mandatory_example(self):
        response = extract_missing_mandatory_param_example({'parent': {'mandatory_param': 'Hello!'}})

        self.assertEqual('Here!', response)

    def test_extract_from_json_example(self):
        dictionary = {
            'parent': '{"my_param": "Hello!" }',
            'other': 'other value'
        }

        self.assertEqual('Hello!', extract_from_json_example(dictionary))

    def test_extract_from_event_example(self):
        event = {
            'body': '{"my_param": "Hello!"}',
            'headers': {
                'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9l'
                                 'IiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
            }
        }

        self.assertEqual(('Hello!', '1234567890'), extract_from_event_example(event, None))

    def test_extract_from_context_example(self):
        context = {
            'parent': {
                'my_param': 'Hello!'
            }
        }

        self.assertEqual('Hello!', extract_from_context_example(None, context))

    @patch("boto3.client")
    def test_extract_from_ssm_example(self, mock_boto_client):
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

        self.assertEqual((None, 'test1', 'test2'), extract_from_ssm_example(None))

    def test_validate_example(self):
        self.assertEqual(('Hello!', '123456'), validate_example('Hello!', '123456'))

    def test_validate_raises_exception_example(self):
        self.assertEqual({'statusCode': 400, 'body': 'Error validating parameters'}, validate_example('Hello!', 'ABCD'))

    @staticmethod
    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_log_example(mock_logger):
        log_example('Hello!')  # logs 'Hello!' and 'Done!'

        mock_logger.info.assert_has_calls([
            call('Parameters: %s', ('Hello!',)),
            call('Response: %s', 'Done!')
        ])

    @patch("boto3.resource")
    def test_handle_exceptions_example(self, mock_dynamo):
        mock_table = MagicMock()
        client_error = ClientError({}, '')
        mock_table.query.side_effect = client_error

        mock_dynamo.return_value.Table.return_value = mock_table

        response = handle_exceptions_example()

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response['body'], 'Your message when a client error happens.')

    def test_response_as_json_example(self):

        self.assertEqual('{"param": "hello!"}', response_body_as_json_example()['body'])
