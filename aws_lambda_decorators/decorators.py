import json
import logging
import boto3
from aws_lambda_decorators.utils import full_name


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def extract_from_event(parameters):
    return extract(parameters)


def extract_from_context(parameters):
    for param in parameters:
        param.func_param_index = 1
    return extract(parameters)


def extract(parameters):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                for param in parameters:
                    kwargs[param.get_var_name()] = param.get_value_by_path(args)
                return func(*args, **kwargs)
            except Exception as ex:  # noqa: pylint - broad-except
                LOGGER.error(f"{full_name(ex)}: '{ex}' in index {param.func_param_index} for path {param.path}")  # noqa: pylint - logging-fstring-interpolation
                return {
                    'statusCode': 400,
                    'body': 'Error extracting parameters'
                }
        return wrapper
    return decorator


def handle_exceptions(handlers):
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
    def decorator(func):
        def wrapper(*args, **kwargs):
            if parameters:
                LOGGER.info(*args)
            func_response = func(*args, **kwargs)
            if response:
                LOGGER.info(func_response)
            return func_response
        return wrapper
    return decorator


def extract_from_ssm(ssm_parameters):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ssm = boto3.client("ssm")
            server_key_containers = ssm.get_parameters(
                Names=[ssm_parameter.get_ssm_name() for ssm_parameter in ssm_parameters],
                WithDecryption=True)
            for idx, key_container in enumerate(server_key_containers['Parameters']):
                kwargs[ssm_parameters[idx].get_var_name()] = key_container['Value']
            return func(*args, **kwargs)
        return wrapper
    return decorator


def response_body_as_json(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if 'body' in response:
            try:
                response['body'] = json.dumps(response['body'])
            except TypeError:
                return {'responseCode': 500, 'body': 'Response body is not JSON serializable'}
        return response
    return wrapper
