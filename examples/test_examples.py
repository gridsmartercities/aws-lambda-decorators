import unittest
from aws_lambda_decorators.decorators import extract
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
            return [my_param, missing_non_mandatory, missing_mandatory, user_id]

        self.assertEqual(['Hello!', 'I am missing', None, '123'], lambda_handler(a_dictionary, another_dictionary))

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
