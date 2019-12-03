# flake8: noqa
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from schema import Schema, Or
from aws_lambda_decorators import (extract, extract_from_event, extract_from_context, extract_from_ssm, validate, log,
                                   handle_exceptions, response_body_as_json, Parameter, SSMParameter,
                                   ValidatedParameter, ExceptionHandler, Mandatory, RegexValidator,
                                   handle_all_exceptions, cors, SchemaValidator, Maximum, Minimum, Type, EnumValidator,
                                   NonEmpty, DateValidator, CurrencyValidator)


@extract(parameters=[
            # extracts a non mandatory my_param from a_dictionary
            Parameter(path="/parent/my_param", func_param_name="a_dictionary"),
            # extracts a non mandatory missing_non_mandatory from a_dictionary
            Parameter(path="/parent/missing_non_mandatory", func_param_name="a_dictionary"),
            # does not fail as the parameter is not validated as mandatory
            Parameter(path="/parent/missing_mandatory", func_param_name="a_dictionary"),
            # extracts a mandatory id as "user_id" from another_dictionary
            Parameter(path="/parent/child/id", validators=[Mandatory], var_name="user_id",
                      func_param_name="another_dictionary")
        ])
def extract_example(a_dictionary, another_dictionary, my_param="aDefaultValue",
                    missing_non_mandatory="I am missing", missing_mandatory=None, user_id=None):
    #  you can now access the extracted parameters directly:
    return my_param, missing_non_mandatory, missing_mandatory, user_id


@extract(parameters=[
            # extracts a non mandatory my_param from a_dictionary
            Parameter(path="/parent/my_param", func_param_name="a_dictionary")
        ])
def extract_to_kwargs_example(a_dictionary, **kwargs):
    return kwargs["my_param"]


@extract(parameters=[
            # extracts a mandatory my_param from a_dictionary
            Parameter(path="/parent/mandatory_param", func_param_name="a_dictionary", validators=[Mandatory])
        ])
def extract_mandatory_param_example(a_dictionary, mandatory_param=None):
    return "Here!"  # this part will never be reached, if the mandatory_param is missing


@extract(parameters=[
    # extracts two mandatory parameters from a_dictionary
    Parameter(path="/parent/mandatory_param", func_param_name="a_dictionary", validators=[Mandatory]),
    Parameter(path="/parent/another_mandatory_param", func_param_name="a_dictionary", validators=[Mandatory]),
    Parameter(path="/parent/an_int", func_param_name="a_dictionary", validators=[Maximum(10), Minimum(5)])
], group_errors=True)  # groups both errors together
def extract_multiple_param_example(a_dictionary, mandatory_param=None, another_mandatory_param=None, an_int=0):
    return "Here!"  # this part will never be reached, if the mandatory_param is missing


@extract(parameters=[
    # extracts a non mandatory my_param from a_dictionary
    Parameter(path="/parent[json]/my_param", func_param_name="a_dictionary")
])
def extract_from_json_example(a_dictionary, my_param=None):
    return my_param


@extract_from_event(parameters=[
            # extracts a mandatory my_param from the json body of the event
            Parameter(path="/body[json]/my_param", validators=[Mandatory]),
            # extract the mandatory sub value as user_id from the authorization JWT
            Parameter(path="/headers/Authorization[jwt]/sub", validators=[Mandatory], var_name="user_id")
        ])
def extract_from_event_example(event, context, my_param=None, user_id=None):
    return my_param, user_id  # returns ("Hello!", "1234567890")


@extract_from_context(parameters=[
    # extracts a mandatory my_param from the parent element in context
    Parameter(path="/parent/my_param", validators=[Mandatory])
])
def extract_from_context_example(event, context, my_param=None):
    return my_param  # returns "Hello!"


@extract_from_ssm(ssm_parameters=[
            # extracts the value of one_key from SSM as a kwarg named "one_key"
            SSMParameter(ssm_name="one_key"),
            # extracts another_key as a kwarg named "another"
            SSMParameter(ssm_name="another_key", var_name="another")
        ])
def extract_from_ssm_example(your_func_params, one_key=None, another=None):
    return your_func_params, one_key, another


@validate(parameters=[
    # validates a_param as mandatory
    ValidatedParameter(func_param_name="a_param", validators=[Mandatory]),
    # validates another_param as mandatory and containing only digits
    ValidatedParameter(func_param_name="another_param", validators=[Mandatory, RegexValidator(r"\d+")]),
    # validates param_with_schema as an object with specified schema
    ValidatedParameter(func_param_name="param_with_schema", validators=[SchemaValidator(Schema({"a": Or(str, dict)}))])
])
def validate_example(a_param, another_param, param_with_schema):
    return a_param, another_param, param_with_schema  # returns a_param, another_param, param_with_schema


@log(parameters=True, response=True)
def log_example(parameters):
    return "Done!"


@handle_exceptions(handlers=[
            ExceptionHandler(ClientError, "Your message when a client error happens.")
        ])
def handle_exceptions_example():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("your_table_name")
    table.query(KeyConditionExpression=Key("user_id").eq("1234"))
    # ...


@response_body_as_json
def response_body_as_json_example():
    return {"statusCode": 400, "body": {"param": "hello!"}}


@extract(parameters=[
    # extracts a non mandatory my_param from a_dictionary
    Parameter(path="/parent[1]/my_param", func_param_name="a_dictionary")
])
def extract_from_list_example(a_dictionary, my_param=None):
    return my_param


@handle_all_exceptions()
def handle_all_exceptions_example():
    test_list = [1, 2, 3]
    test_list[5]
    # ...


@cors(allow_origin="*", allow_methods="POST", allow_headers="Content-Type", max_age=86400)
def cors_example():
    return {"statusCode": 200}


@extract(parameters=[
    Parameter(path="/parent/an_int", func_param_name="a_dictionary",
              validators=[Minimum(100, "Bad value {value}: should be at least {condition}")])
])
def extract_minimum_param_with_custom_error_example(a_dictionary, an_int=None):
    return {}


@extract(parameters=[
    Parameter(path="/params/my_param_1", func_param_name="a_dictionary"),
    Parameter(path="/params/my_param_2", func_param_name="a_dictionary")
])
def extract_dictionary_example(a_dictionary, **kwargs):
    return kwargs


@extract(parameters=[
    Parameter(path="/params/a_bool", func_param_name="a_dictionary", validators=[Type(bool)])
])
def extract_type_param(a_dictionary, a_bool=False):
    return a_bool


@extract(parameters=[
    Parameter(path="/params/an_enum", func_param_name="a_dictionary", validators=[EnumValidator("Hello", "Bye")])
])
def extract_enum_param(a_dictionary, an_enum=None):
    return an_enum


@extract(parameters=[
    Parameter(path="/params/non_empty", func_param_name="a_dictionary", validators=[NonEmpty])
])
def extract_non_empty_param(a_dictionary, non_empty=None):
    return non_empty


@extract(parameters=[
    Parameter(path="/params/date_example", func_param_name="a_dictionary",
              validators=[DateValidator("%Y-%m-%d %H:%M:%S")])
])
def extract_date_param(a_dictionary, date_example=None):
    return date_example


@extract(parameters=[
    Parameter(path="/params/my_param", func_param_name="a_dictionary", transform=int)
])
def extract_with_transform_example(a_dictionary, my_param=None):
    return my_param


def to_int(arg):
    try:
        return int(arg)
    except Exception:
        raise Exception("My custom error message")


@extract(parameters=[
    Parameter(path="/params/my_param", func_param_name="a_dictionary", transform=to_int)
])
def extract_with_custom_transform_example(a_dictionary, my_param=None):
    return {}


@extract(parameters=[
    Parameter(path="/params/currency_example", func_param_name="a_dictionary",
              validators=[CurrencyValidator])
])
def extract_currency_param(a_dictionary, currency_example=None):
    return currency_example
