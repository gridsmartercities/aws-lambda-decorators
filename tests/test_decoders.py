# pylint:disable=no-self-use
import json
import unittest
from unittest.mock import patch
from aws_lambda_decorators.decoders import decode, decode_json, decode_jwt
from aws_lambda_decorators.decorators import extract
from aws_lambda_decorators.classes import Parameter


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


class DecodersTests(unittest.TestCase):

    @patch("aws_lambda_decorators.decoders.LOGGER")
    def test_decode_function_missing_logs_error(self, mock_logger):
        decode("[random]", None)
        mock_logger.error.assert_called_once_with("Missing decode function for annotation: %s", "[random]")

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_returns_400_on_json_decode_error(self, mock_logger):
        path = "/a/b[json]/c"
        dictionary = {
            "a": {
                "b": "{'c'}"
            }
        }

        @extract([Parameter(path, "event")])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertEqual("{\"message\": \"Error extracting parameters\"}", response["body"])

        mock_logger.error.assert_called_once_with(
            "%s: %s in argument %s for path %s",
            "json.decoder.JSONDecodeError",
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            "event",
            "/a/b[json]/c")

    @patch("aws_lambda_decorators.decorators.LOGGER")
    def test_extract_returns_400_on_jwt_decode_error(self, mock_logger):
        path = "/a/b[jwt]/c"
        dictionary = {
            "a": {
                "b": "wrong.jwt"
            }
        }

        @extract([Parameter(path, "event")])
        def handler(event, context, c=None):  # noqa
            return {}

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])
        self.assertTrue("{\"message\": \"Error extracting parameters\"}" in response["body"])

        mock_logger.error.assert_called_once_with(
            "%s: %s in argument %s for path %s",
            "jwt.exceptions.DecodeError",
            "Not enough segments",
            "event",
            "/a/b[jwt]/c")

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

        @extract([Parameter(path, "event")])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)

        self.assertEqual(3, response)

    @patch("aws_lambda_decorators.decorators.LOGGER")
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

        @extract([Parameter(path, "event")])
        def handler(event, context, c=None):  # noqa
            return c

        response = handler(dictionary, None)

        self.assertEqual(400, response["statusCode"])  # noqa
        self.assertTrue("{\"message\": \"Error extracting parameters\"}" in response["body"])  # noqa

        mock_logger.error.assert_called_once_with(
            "%s: %s in argument %s for path %s",
            "IndexError",
            "list index out of range",
            "event",
            "/a/b[4]/c")

    def test_extract_multiple_parameters_from_json_hits_cache(self):
        dictionary = {
            "a": json.dumps({
                "b": 123,
                "c": 456
            })
        }

        initial_cache_info = decode_json.cache_info()

        @extract([
            Parameter("a[json]/b", "event", var_name="b"),
            Parameter("a[json]/c", "event", var_name="c")
        ])  # noqa: pylint - invalid-name
        def handler(event, b=None, c=None):  # noqa: pylint - unused-argument
            return {}

        handler(dictionary)

        self.assertEqual(decode_json.cache_info().hits, initial_cache_info.hits + 1)
        self.assertEqual(decode_json.cache_info().misses, initial_cache_info.misses + 1)
        self.assertEqual(decode_json.cache_info().currsize, initial_cache_info.currsize + 1)

    def test_extract_multiple_parameters_from_jwt_hits_cache(self):
        dictionary = {
            "a": TEST_JWT
        }

        initial_cache_info = decode_jwt.cache_info()

        @extract([
            Parameter("a[jwt]/sub", "event", var_name="sub"),
            Parameter("a[jwt]/aud", "event", var_name="aud")
        ])
        def handler(event, sub=None, aud=None):  # noqa: pylint - unused-argument
            return {}

        handler(dictionary)

        self.assertEqual(decode_jwt.cache_info().hits, initial_cache_info.hits + 1)
        self.assertEqual(decode_jwt.cache_info().misses, initial_cache_info.misses + 1)
        self.assertEqual(decode_jwt.cache_info().currsize, initial_cache_info.currsize + 1)
