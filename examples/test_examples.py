import unittest
from unittest.mock import patch, MagicMock
from aws_lambda_decorators.decorators import extract, extract_from_event, extract_from_context, extract_from_ssm, \
    validate
from aws_lambda_decorators.classes import Parameter, SSMParameter, ValidatedParameter
from aws_lambda_decorators.validators import Mandatory, RegexValidator


class ExamplesTests(unittest.TestCase):

    def test_extract_example(self):
        #  Given these two dictionaries:
        a_dictionary = {
            'parent': {
                'my_param': 'Hello!'
            },
            'other': 'other value'
        }
        another_dictionary = {
            'parent': {
                'child': {
                    'id': '123'
                }
            }
        }

        @extract(parameters=[
            Parameter(path='/parent/my_param', func_param_name='a_dictionary'),
            # extracts a non mandatory my_param from a_dictionary
            Parameter(path='/parent/missing_non_mandatory', func_param_name='a_dictionary', default='I am missing'),
            # extracts a non mandatory missing_non_mandatory from a_dictionary
            Parameter(path='/parent/missing_mandatory', func_param_name='a_dictionary'),
            # does not fail as the parameter is not validated as mandatory
            Parameter(path='/parent/child/id', validators=[Mandatory], var_name='user_id',
                      func_param_name='another_dictionary')
            # extracts a mandatory id as "user_id" from another_dictionary
        ])
        def lambda_handler(a_dictionary, another_dictionary, my_param='aDefaultValue',
                           missing_non_mandatory='I am missing', missing_mandatory=None, user_id=None):
            #  you can now access the extracted parameters directly:
            return my_param, missing_non_mandatory, missing_mandatory, user_id

        self.assertEqual(('Hello!', 'I am missing', None, '123'), lambda_handler(a_dictionary, another_dictionary))

    def test_extract_to_kwrags_example(self):
        dictionary = {
            'parent': {
                'my_param': 'Hello!'
            },
            'other': 'other value'
        }

        @extract(parameters=[
            Parameter(path='/parent/my_param', func_param_name='a_dictionary'),
            # extracts a non mandatory my_param from a_dictionary
        ])
        def lambda_handler(a_dictionary, **kwargs):
            return kwargs['my_param']

        self.assertEqual('Hello!', lambda_handler(dictionary))

    def test_extract_missing_mandatory_example(self):
        @extract(parameters=[
            Parameter(path='/parent/mandatory_param', func_param_name='a_dictionary', validators=[Mandatory]),
            # extracts a mandatory my_param from a_dictionary
        ])
        def lambda_handler(a_dictionary, mandatory_param=None):
            print('Here!')  # this message will never be reached

        response = lambda_handler({'parent': {'my_param': 'Hello!'}, 'other': 'other value'})

        self.assertEqual({'statusCode': 400, 'body': 'Error extracting parameters'}, response)

    def test_extract_from_json_example(self):
        dictionary = {
            'parent': '{"my_param": "Hello!" }',
            'other': 'other value'
        }

        @extract(parameters=[
            Parameter(path='/parent[json]/my_param', func_param_name='a_dictionary'),
            # extracts a non mandatory my_param from a_dictionary
        ])
        def lambda_handler(a_dictionary, my_param=None):
            return my_param

        self.assertEqual('Hello!', lambda_handler(dictionary))

    def test_extract_from_event_example(self):
        event = {
            'body': '{"my_param": "Hello!"}',
            'headers': {
                'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
            }
        }

        @extract_from_event(parameters=[
            Parameter(path='/body[json]/my_param', validators=[Mandatory]),
            # extracts a mandatory my_param from the json body of the event
            Parameter(path='/headers/Authorization[jwt]/sub', validators=[Mandatory], var_name='user_id')
            # extract the mandatory sub value as user_id from the authorization JWT
        ])
        def api_gateway_lambda_handler(event, context, my_param=None, user_id=None):
            return my_param, user_id  # returns ('Hello!', '1234567890')

        self.assertEqual(('Hello!', '1234567890'), api_gateway_lambda_handler(event, None))

    def test_extract_from_context_example(self):
        context = {
            'parent': {
                'my_param': 'Hello!'
            }
        }

        @extract_from_context(parameters=[
            Parameter(path='/parent/my_param', validators=[Mandatory]),
            # extracts a mandatory my_param from the parent element in context
        ])
        def api_gateway_lambda_handler(event, context, my_param=None):
            return my_param  # returns 'Hello!'

        self.assertEqual('Hello!', api_gateway_lambda_handler(None, context))

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

        @extract_from_ssm(ssm_parameters=[
            SSMParameter(ssm_name='one_key'),  # extracts the value of one_key from SSM as a kwarg named "one_key"
            SSMParameter(ssm_name='another_key', var_name="another"),  # extracts another_key as a kwarg named "another"
        ])
        def your_function(your_func_params, one_key=None, another=None):
            return your_func_params, one_key, another

        self.assertEqual((None, 'test1', 'test2'), your_function(None))

    def test_validate_example(self):
        @validate(parameters=[
            ValidatedParameter(func_param_name='a_param', validators=[Mandatory]),  # validates a_param as mandatory
            ValidatedParameter(func_param_name='another_param', validators=[Mandatory, RegexValidator(r'\d+')])
            # validates another_param as mandatory and containing only digits
        ])
        def your_function(a_param, another_param):
            return a_param, another_param  # returns a_param, another_param

        self.assertEqual(('Hello!', '123456'), your_function('Hello!', '123456'))

    def test_validate_raises_exception_example(self):
        @validate(parameters=[
            ValidatedParameter(func_param_name='a_param', validators=[Mandatory]),  # validates a_param as mandatory
            ValidatedParameter(func_param_name='another_param', validators=[Mandatory, RegexValidator(r'\d+')])
            # validates another_param as mandatory and containing only digits
        ])
        def your_function(a_param, another_param):
            return a_param, another_param  # returns a_param, another_param

        self.assertEqual({'statusCode': 400, 'body': 'Error validating parameters'}, your_function('Hello!', 'ABCD'))
