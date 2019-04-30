# pylint:disable=no-self-use
import unittest
from unittest.mock import patch
from aws_lambda_decorators.decoders import decode
from aws_lambda_decorators.decorators import extract
from aws_lambda_decorators.classes import Parameter


class DecodersTests(unittest.TestCase):

    @patch('aws_lambda_decorators.decoders.LOGGER')
    def test_decode_function_missing_logs_error(self, mock_logger):
        decode('[random]', None)
        mock_logger.error.assert_called_once_with('Missing decode function for annotation: %s', '[random]')

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_extract_returns_400_on_json_decode_error(self, mock_logger):
        path = "/a/b[json]/c"
        dictionary = {
            "a": {
                "b": "{'c'}"
            }
        }

        @extract([Parameter(path, 'event')])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual('{"message": "Error extracting parameters"}', response["body"])

        mock_logger.error.assert_called_once_with("%s: '%s' in argument %s for path %s",
                                                  'json.decoder.JSONDecodeError',
                                                  'Expecting property name enclosed in double quotes: line 1 column 2 '
                                                  '(char 1)',
                                                  'event',
                                                  '/a/b[json]/c')

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_extract_returns_400_on_jwt_decode_error(self, mock_logger):
        path = "/a/b[jwt]/c"
        dictionary = {
            "a": {
                "b": "wrong.jwt"
            }
        }

        @extract([Parameter(path, 'event')])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertTrue('{"message": "Error extracting parameters"}' in response["body"])

        mock_logger.error.assert_called_once_with("%s: '%s' in argument %s for path %s",
                                                  'jwt.exceptions.DecodeError',
                                                  'Not enough segments',
                                                  'event',
                                                  '/a/b[jwt]/c')

    def test_extracts_from_list_by_index_annotation_successfully(self):
        path = "/a/b[1]/c"
        dictionary = {
            "a": {
                "b": [
                    {
                        "c": 2
                    },
                    {
                        "c": 3
                    }
                ]
            }
        }

        @extract([Parameter(path, 'event')])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)

        self.assertEqual(3, response)

    @patch('aws_lambda_decorators.decorators.LOGGER')
    def test_extracts_from_list_by_index_out_of_range_fails_with_400(self, mock_logger):
        path = "/a/b[4]/c"
        dictionary = {
            "a": {
                "b": [
                    {
                        "c": 2
                    },
                    {
                        "c": 3
                    }
                ]
            }
        }

        @extract([Parameter(path, 'event')])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])  # noqa
        self.assertTrue('{"message": "Error extracting parameters"}' in response["body"])  # noqa

        mock_logger.error.assert_called_once_with("%s: '%s' in argument %s for path %s",
                                                  'IndexError',
                                                  'list index out of range',
                                                  'event',
                                                  '/a/b[4]/c')
