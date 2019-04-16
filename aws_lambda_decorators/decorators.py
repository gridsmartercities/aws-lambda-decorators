"""
AWS lambda decorators.

A set of Python decorators to ease the development of AWS lambda functions.

"""
import json
import logging
import boto3
from aws_lambda_decorators.utils import full_name, all_func_args


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

BODY_NOT_JSON_ERROR = 'Response body is not JSON serializable'
PARAM_EXTRACT_ERROR = 'Error extracting parameters'
PARAM_EXTRACT_LOG_MESSAGE = "%s: '%s' in argument %s for path %s"
PARAM_INVALID_ERROR = "Error validating parameters"
PARAM_LOG_MESSAGE = "Parameters: %s"
RESPONSE_LOG_MESSAGE = "Response: %s"


def extract_from_event(parameters):
    """
    Extracts a set of parameters from the event dictionary in a lambda handler.

    The extracted parameters are added as kwargs to the handler function.

    Usage:
        @extract_from_event([Parameter(path='/body[json]/my_param')])
        def lambda_handler(event, context, my_param=None)
            pass
    """
    for param in parameters:
        param.func_param_name = 'event'
    return extract(parameters)


def extract_from_context(parameters):
    """
    Extracts a set of parameters from the context dictionary in a lambda handler.

    The extracted parameters are added as kwargs to the handler function.

    Usage:
        @extract_from_context([Parameter(path='/parent/my_param')])
        def lambda_handler(event, context, my_param=None)
            pass
    """
    for param in parameters:
        param.func_param_name = 'context'
    return extract(parameters)


def extract(parameters):
    """
    Extracts a set of parameters from any function parameter passed to an AWS lambda handler.

    The extracted parameters are added as kwargs to the handler function.

    Usage:
        @extract([Parameter(path='headers/Authorization[jwt]/sub', var_name='user_id', func_param_name='event')])
        def lambda_handler(event, context, user_id=None)
            pass

    Args:
        parameters (list): A collection of Parameter type items.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                arg_dictionary = all_func_args(func, args, kwargs)
                for param in parameters:
                    param_val = arg_dictionary[param.func_param_name]
                    return_val = param.extract_validated_value(param_val)
                    if return_val is not None:
                        kwargs[param.get_var_name()] = return_val
            except Exception as ex:  # noqa: pylint - broad-except
                LOGGER.error(PARAM_EXTRACT_LOG_MESSAGE, full_name(ex), str(ex), param.func_param_name, param.path)  # noqa: pylint - logging-fstring-interpolation
                return {
                    'statusCode': 400,
                    'body': PARAM_EXTRACT_ERROR
                }
            return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_exceptions(handlers):
    """
    Handles exceptions thrown by the wrapped/decorated function.

    Usage:
        @handle_exceptions([ExceptionHandler(exception=KeyError, friendly_message='Your message on KeyError except')]).
        def lambda_handler(params)
            pass

    Args:
        handlers (list): A collection of ExceptionHandler type items.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple([handler.exception for handler in handlers]) as ex:  # noqa: pylint - catching-non-exception
                message = [handler.friendly_message for handler in handlers if handler.exception is type(ex)][0]
                log_message = message if str(ex) == '' else message + ': ' + str(ex)
                LOGGER.error(log_message)
                return {
                    'statusCode': 400,
                    'body': message
                }
        return wrapper
    return decorator


def log(parameters=False, response=False):
    """Log parameters and/or response of the wrapped/decorated function using logging package."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if parameters:
                LOGGER.info(PARAM_LOG_MESSAGE, args)
            func_response = func(*args, **kwargs)
            if response:
                LOGGER.info(RESPONSE_LOG_MESSAGE, func_response)
            return func_response
        return wrapper
    return decorator


def extract_from_ssm(ssm_parameters):
    """
    Load given ssm parameters from AWS parameter store to the handler variables.

    Usage:
        @extract_from_ssm([SSMParameter(ssm_name='key', var_name='var')])
        def lambda_handler(var=None)
            pass

    Args:
        ssm_parameters (list): A collection of SSMParameter type items.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            ssm = boto3.client('ssm')
            server_key_containers = ssm.get_parameters(
                Names=[ssm_parameter.get_ssm_name() for ssm_parameter in ssm_parameters],
                WithDecryption=True)
            for key_container in server_key_containers['Parameters']:
                for ssm_parameter in ssm_parameters:  # pragma: no cover
                    if ssm_parameter.get_ssm_name() == key_container['Name']:
                        kwargs[ssm_parameter.get_var_name()] = key_container['Value']
                        break
            return func(*args, **kwargs)
        return wrapper
    return decorator


def response_body_as_json(func):
    """
    Convert the dictionary response of the wrapped/decorated function to a json string literal.

    Usage:
        @response_body_as_json
        def lambda_handler():
            return {'responseCode': 200, 'body': {'key': 'value'}}

        will return {'responseCode': 200, 'body': "{'key':'value'}"}
    """
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if 'body' in response:
            try:
                response['body'] = json.dumps(response['body'])
            except TypeError:
                return {'responseCode': 500, 'body': BODY_NOT_JSON_ERROR}
        return response
    return wrapper


def validate(parameters):
    """
    Validates a set of function parameters.

    Usage:
        @validate([ValidatedParameter(func_param_name='my_param', validators=[...])])
        def func(my_param)
            pass

    Args:
        parameters (list): A collection of ValidatedParameter type items.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            arg_dictionary = all_func_args(func, args, kwargs)
            for param in parameters:
                if not param.validate(arg_dictionary[param.func_param_name]):
                    return {
                        'statusCode': 400,
                        'body': PARAM_INVALID_ERROR
                    }
            return func(*args, **kwargs)
        return wrapper
    return decorator
