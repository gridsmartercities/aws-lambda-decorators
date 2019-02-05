"""
AWS lambda decorators.

Something something.
"""
import json
import logging
import boto3
from aws_lambda_decorators.utils import full_name


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

BODY_NOT_JSON_ERROR = 'Response body is not JSON serializable'
PARAM_EXTRACT_ERROR = 'Error extracting parameters'
PARAM_EXTRACT_LOG_MESSAGE = "%s: '%s' in index %s for path %s"


def extract_from_event(parameters):
    """
    Extract given parameters from the event dictionary in the lambda handler to the handler variables.

    Usage: see extract.
    """
    return extract(parameters)


def extract_from_context(parameters):
    """
    Extract given parameters from the context dictionary in the lambda handler to the handler variables.

    Usage: see extract.
    """
    for param in parameters:
        param.func_param_index = 1
    return extract(parameters)


def extract(parameters):
    """
    Extract given parameters from either event or context dictionaries in the lambda handler to the handler variables.

    Usage:
        @extract[_from_event|_from_context]([Parameter('a/b[jwt]/c', 'var')])
        def myFunction(event, context, var=None)

    Args:
        parameters (list): A collection of Parameter type items.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                for param in parameters:
                    kwargs[param.get_var_name()] = param.get_value_by_path(args)
                return func(*args, **kwargs)
            except Exception as ex:  # noqa: pylint - broad-except
                LOGGER.error(PARAM_EXTRACT_LOG_MESSAGE, full_name(ex), str(ex), param.func_param_index, param.path)  # noqa: pylint - logging-fstring-interpolation
                return {
                    'statusCode': 400,
                    'body': PARAM_EXTRACT_ERROR
                }
        return wrapper
    return decorator


def handle_exceptions(handlers):
    """
    Handle exceptions thrown by the wrapped/decorated function.

    Usage:
        @handle_exceptions([ExceptionHandler(KeyError, 'Your message on KeyError except')]).
        def myFunction(...)

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
                LOGGER.info(args)
            func_response = func(*args, **kwargs)
            if response:
                LOGGER.info(func_response)
            return func_response
        return wrapper
    return decorator


def extract_from_ssm(ssm_parameters):
    """
    Load given ssm parameters from AWS parameter store to the handler variables.

    Usage:
        @extract_from_ssm([SSMParameter('key', 'var')])
        def myFunction(var=None)

    Args:
        ssm_parameters (list): A collection of SSMParameter type items.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            ssm = boto3.client('ssm')
            server_key_containers = ssm.get_parameters(
                Names=[ssm_parameter.get_ssm_name() for ssm_parameter in ssm_parameters],
                WithDecryption=True)
            for idx, key_container in enumerate(server_key_containers['Parameters']):
                kwargs[ssm_parameters[idx].get_var_name()] = key_container['Value']
            return func(*args, **kwargs)
        return wrapper
    return decorator


def response_body_as_json(func):
    """
    Convert the dictionary response of the wrapped/decorated function to a json string literal.

    Usage:
        @response_body_as_json
        def myFunc():
            return {'responseCode': 200, 'body': {'a'}}
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
