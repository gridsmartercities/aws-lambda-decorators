import unittest
from aws_lambda_decorators.decorators import extract, extract_from_event
from aws_lambda_decorators.classes import Parameter
from aws_lambda_decorators.validators import Mandatory


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
