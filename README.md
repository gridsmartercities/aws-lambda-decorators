[<img align="right" alt="Grid Smarter Cities" src="https://s3.eu-west-2.amazonaws.com/open-source-resources/grid_smarter_cities_small.png">](https://www.gridsmartercities.com/)

![Build Status](https://codebuild.eu-west-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiSTZNdEsxUHdnWWdRMGwrS3FuaUxSb0g5c2hNdWdSNE94Y1RFRGNrdk96Zm9LWlZWWmpEK1FTWmcraGRnMEdzbmRjakF5SDVQUVBzcVpNL3hLSGw3TnpNPSIsIml2UGFyYW1ldGVyU3BlYyI6ImZsbHEwcUJGOFV2VXNpWHoiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Github Release](https://img.shields.io/github/release/gridsmartercities/aws-lambda-decorators.svg?style=flat)
\
\
![Python Versions](https://img.shields.io/pypi/pyversions/aws-lambda-decorators.svg?style=flat)
![PyPi Version](https://img.shields.io/pypi/v/aws-lambda-decorators.svg?style=flat)
![PyPi Status](https://img.shields.io/pypi/status/aws-lambda-decorators.svg?style=flat)
![Pypi Downloads](https://img.shields.io/pypi/dm/aws-lambda-decorators.svg?style=flat&logo=pypi)

# aws-lambda-decorators

A set of Python decorators to ease the development of AWS lambda functions.

## Installation

The easiest way to use these AWS Lambda Decorators is to install them through Pip:

`pip install aws-lambda-decorators`

## Package Contents

### [Decorators](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py)

The current list of AWS Lambda Python Decorators includes:

* [__extract__](#extract): a decorator to extract and validate specific keys of a dictionary parameter passed to a AWS Lambda function.
* [__extract_from_event__](#extract_from_event): a facade of [__extract__](#extract) to extract and validate keys from an AWS API Gateway lambda function _event_ parameter.
* [__extract_from_context__](#extract_from_context): a facade of [__extract__](#extract) to extract and validate keys from an AWS API Gateway lambda function _context_ parameter.
* [__extract_from_ssm__](#extract_from_ssm): a decorator to extract from AWS SSM the values of a set of parameter keys.
* [__validate__](#validate): a decorator to validate a list of function parameters.
* [__log__](#log): a decorator to log the parameters passed to the lambda function and/or the response of the lambda function.
* [__handle_exceptions__](#handle_exceptions): a decorator to handle any type of declared exception generated by the lambda function. 
* [__response_body_as_json__](#response_body_as_json): a decorator to transform a response dictionary body to a json string.
* [__handle_all_exceptions__](#handle_all_exceptions): a decorator to handle all exceptions thrown by the lambda function.
* [__cors__](#cors): a decorator to add cors headers to a lambda function.


### [Validators](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/validators.py)

Currently, the package offers 3 validators:

* [__Mandatory__](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/validators.py#L5-L16): Checks if a parameter has a value.
* [__RegexValidator__](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/validators.py#L19-L38): Checks a parameter against a regular expression.
* [__SchemaValidator__](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/validators.py#L41-L63): Checks if an object adheres to the schema. Uses [schema](https://github.com/keleshev/schema) library.
* [__Minimum__](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/validators.py#L66-L91): Checks if an optional numerical value is greater than a minimum value.
* [__Maximum__](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/validators.py#L94-L119): Checks if an optional numerical value is less than a maximum value.

### [Decoders](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decoders.py)

The package offers functions to decode from JSON and JWT. 

* [__decode_json__](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decoders.py#L48-L50): decodes/converts a json string to a python dictionary
* [__decode_jwt__](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decoders.py#L53-L55): decodes/converts a JWT string to a python dictionary

## Examples

### extract

This decorator extracts and validates values from dictionary parameters passed to a Lambda Function.

* The decorator takes a list of [Parameter](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L109-L207) objects.
* Each [Parameter](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L109-L207) object requires a non-empty path to the parameter in the dictionary, and the name of the dictionary (func_param_name)
* The parameter value is extracted and added as a kwarg to the lambda handler (or any other decorated function/method).
* You can add the parameter to the handler signature, or access it in the handler through kwargs.
* The name of the extracted parameter is defaulted to the last element of the path name, but can be changed by passing a (valid pythonic variable name) var_name
* You can define a default value for the parameter in the [Parameter](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L109-L207) or in the lambda handler itself.
* A 400 exception is raised when the parameter cannot be extracted or when it does not validate.
* A variable path (e.g. '/headers/Authorization[jwt]/sub') can be annotated to specify a decoding. In the example, Authorization might contain a JWT, which needs to be decoded before accessing the "sub" element.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L11-L25) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L12-L32)
```python
@extract(parameters=[
    Parameter(path='/parent/my_param', func_param_name='a_dictionary'),  # extracts a non mandatory my_param from a_dictionary
    Parameter(path='/parent/missing_non_mandatory', func_param_name='a_dictionary', default='I am missing'),  # extracts a non mandatory missing_non_mandatory from a_dictionary
    Parameter(path='/parent/missing_mandatory', func_param_name='a_dictionary'),  # does not fail as the parameter is not validated as mandatory
    Parameter(path='/parent/child/id', validators=[Mandatory], var_name='user_id', func_param_name='another_dictionary')  # extracts a mandatory id as "user_id" from another_dictionary
])
def extract_example(a_dictionary, another_dictionary, my_param='aDefaultValue', missing_non_mandatory='I am missing', missing_mandatory=None, user_id=None):
    """
        Given these two dictionaries:
        
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
    
        you can now access the extracted parameters directly: 
    """
    return my_param, missing_non_mandatory, missing_mandatory, user_id
```

Or you can use kwargs instead of specific parameter names:

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L28-L33) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L33-L46)
```python
@extract(parameters=[
    Parameter(path='/parent/my_param', func_param_name='a_dictionary')  # extracts a non mandatory my_param from a_dictionary
])
def extract_to_kwargs_example(a_dictionary, **kwargs):
    """
        a_dictionary = { 
            'parent': { 
                'my_param': 'Hello!' 
            }, 
            'other': 'other value' 
        }
    """
    return kwargs['my_param']  # returns 'Hello!'
```

A missing mandatory parameter, or a parameter that fails validation, will raise an exception:

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L36-L41) | [test 1](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L48-L60) | [test 2](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L62-L74)
```python
@extract(parameters=[
    Parameter(path='/parent/mandatory_param', func_param_name='a_dictionary', validators=[Mandatory])  # extracts a mandatory mandatory_param from a_dictionary
])
def extract_mandatory_param_example(a_dictionary, mandatory_param=None):
    return 'Here!'  # this part will never be reached, if the mandatory_param is missing
    
response = extract_mandatory_param_example({'parent': {'my_param': 'Hello!'}, 'other': 'other value'} )

print(response)  # prints { 'statusCode': 400, 'body': '{"message": "Error extracting parameters"}' } and logs a more detailed error

```

You can decode any part of the parameter path from json or any other existing annotation.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L44-L49) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L76-L87)
```python
@extract(parameters=[
    Parameter(path='/parent[json]/my_param', func_param_name='a_dictionary')  # extracts a non mandatory my_param from a_dictionary
])
def extract_from_json_example(a_dictionary, my_param=None):
    """
        a_dictionary = { 
            'parent': '{"my_param": "Hello!" }', 
            'other': 'other value' 
        }
    """
    return my_param  # returns 'Hello!'

```

You can also use an integer annotation to access an specific list element by index.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L112-L117) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L193-L207)
```python
@extract(parameters=[
    Parameter(path='/parent[1]/my_param', func_param_name='a_dictionary')  # extracts a non mandatory my_param from a_dictionary
])
def extract_from_list_example(a_dictionary, my_param=None):
    """
        a_dictionary = { 
            'parent': [
                {'my_param': 'Hello!'},
                {'my_param': 'Bye!'}
            ]
        }
    """
    return my_param  # returns 'Bye!'

```

### [extract_from_event](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L28-L41)

This decorator is just a facade to the [extract](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L60-L89) method to be used in AWS Api Gateway Lambdas. It automatically extracts from the event lambda parameter.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L52-L59) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L89-L104)
```python
@extract_from_event(parameters=[
    Parameter(path='/body[json]/my_param', validators=[Mandatory]),  # extracts a mandatory my_param from the json body of the event
    Parameter(path='/headers/Authorization[jwt]/sub', validators=[Mandatory], var_name='user_id')  # extract the mandatory sub value as user_id from the authorization JWT
])
def extract_from_event_example(event, context, my_param=None, user_id=None):
    """
        event = { 
            'body': '{"my_param": "Hello!"}', 
            'headers': { 
                'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c' 
            } 
        }
    """
    return my_param, user_id  # returns ('Hello!', '1234567890')
```

### [extract_from_context](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L44-L576)

This decorator is just a facade to the [extract](#extract) method to be used in AWS Api Gateway Lambdas. It automatically extracts from the context lambda parameter.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L62-L67) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L106-L118)
```python
@extract_from_context(parameters=[
    Parameter(path='/parent/my_param', validators=[Mandatory])  # extracts a mandatory my_param from the parent element in context
])
def extract_from_context_example(event, context, my_param=None):
    """
        context = {
            'parent': {
                'my_param': 'Hello!'
            }
        }
    """    
    return my_param  # returns 'Hello!'
```

### [extract_from_ssm](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L136-L161)

This decorator extracts a parameter from AWS SSM and passes the parameter down to your function as a kwarg.

* The decorator takes a list of [SSMParameter](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L54-L70) objects.
* Each [SSMParameter](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L54-L70) object requires the name of the SSM parameter (ssm_name)
* If no var_name is passed in, the extracted value is passed to the function with the ssm_name name

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L70-L77) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L120-L142)
```python
@extract_from_ssm(ssm_parameters=[
    SSMParameter(ssm_name='one_key'),  # extracts the value of one_key from SSM as a kwarg named "one_key"
    SSMParameter(ssm_name='another_key', var_name="another")  # extracts another_key as a kwarg named "another"
])
def extract_from_ssm_example(your_func_params, one_key=None, another=None):
    return your_func_params, one_key, another
```

### [validate](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L186-L209)

This decorator validates a list of non dictionary parameters from your lambda function.

* The decorator takes a list of [ValidatedParameter](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L73-L106) objects.
* Each parameter object needs the name of the lambda function parameter that it is going to be validated, and the list of rules to validate.
* A 400 exception is raised when the parameter does not validate.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L80-L89) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L144-L149)
```python
@validate(parameters=[
    ValidatedParameter(func_param_name='a_param', validators=[Mandatory]),  # validates a_param as mandatory
    ValidatedParameter(func_param_name='another_param', validators=[Mandatory, RegexValidator(r'\d+')])  # validates another_param as mandatory and containing only digits
    ValidatedParameter(func_param_name='param_with_schema', validators=[SchemaValidator(Schema({'a': Or(str, dict)}))])  # validates param_with_schema as an object with specified schema
])
def validate_example(a_param, another_param, param_with_schema):
    return a_param, another_param, param_with_schema  # returns 'Hello!', '123456', {'a': {'b': 'c'}}
    
validate_example('Hello!', '123456', {'a': {'b': 'c'}})
```

Given the same function `validate_example`, a 400 exception is returned if at least one parameter does not validate:

```python
validate_example('Hello!', 'ABCD')  # returns a 400 status code and an error message
```

### [log](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L122-L133)

This decorator allows for logging the function arguments and/or the response.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L92-L94) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L158-L168)
```python
@log(parameters=True, response=True)
def log_example(parameters): 
    return 'Done!'
    
log_example('Hello!')  # logs 'Hello!' and 'Done!'
```

### [handle_exceptions](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L94-L119)

This decorator handles a list of exceptions, returning a 400 response containing the specified friendly message to the caller.

* The decorator takes a list of [ExceptionHandler](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L11-L33) objects.
* Each [ExceptionHandler](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/classes.py#L11-L33) requires the type of exception to check, and an optional friendly message to return to the caller.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L97-L104) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L170-L184)
```python
@handle_exceptions(handlers=[
    ExceptionHandler(ClientError, "Your message when a client error happens.")
])
def handle_exceptions_example():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('non_existing_table')
    table.query(KeyConditionExpression=Key('user_id').eq(user_id))
    # ...
    
handle_exceptions_example()  # returns {'body': '{"message": "Your message when a client error happens."}', 'statusCode': 400}
```

### [handle_all_exceptions](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L212-L232)

This decorator handles all exceptions thrown by a lambda, returning a 400 response and the exception's message.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L120-L124) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L209-L215)
```python
@handle_all_exceptions()
def handle_exceptions_example():
    test_list = [1, 2, 3]
    invalid_value = test_list[5]
    # ...    

handle_all_exceptions_example()  # returns {'body': '{"message": "list index out of range"}, 'statusCode': 400}
```

### [response_body_as_json](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L164-L183)

This decorator ensures that, if the response contains a body, the body is dumped as json.

* Returns a 500 error if the response body cannot be dumped as json.

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L107-L109) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L186-L191)
```python
@response_body_as_json
def response_body_as_json_example():
    return {'statusCode': 400, 'body': {'param': 'hello!'}}
    
response_body_as_json_example()  # returns { 'statusCode': 400, 'body': "{ 'param': 'hello!' }" }
```

### [cors](https://github.com/gridsmartercities/aws-lambda-decorators/blob/master/aws_lambda_decorators/decorators.py#L235-L288)

This decorator adds your defined CORS headers to the decorated function response.

* Returns a 500 error if one or more of the CORS headers have an invalid type

Example: [code](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/src/examples.py#L127-L129) | [test](https://github.com/gridsmartercities/aws-lambda-decorators-examples/blob/master/test/test_examples.py#L217-L227)
```python
@cors(allow_origin='*', allow_methods='POST', allow_headers='Content-Type', max_age=86400)
def cors_example():
    return {'statusCode': 200}
    
cors_example()  # returns {'statusCode': 200, 'headers': {'access-control-allow-origin': '*', 'access-control-allow-methods': 'POST', 'access-control-allow-headers': 'Content-Type', 'access-control-max-age': 86400}}
```

## Documentation

You can get the docstring help by running:  

```bash
>>> from aws_lambda_decorators.decorators import extract
>>> help(extract)
```

## Links

* [PyPi](https://pypi.org/project/aws-lambda-decorators/)
* [Test PyPi](https://test.pypi.org/project/aws-lambda-decorators/)
* [Github](https://github.com/gridsmartercities/aws-lambda-decorators)


[]: 