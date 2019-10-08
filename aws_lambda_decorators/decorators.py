"""
AWS lambda decorators.

A set of Python decorators to ease the development of AWS lambda functions.

"""
import json
from http import HTTPStatus
import boto3
from aws_lambda_decorators.utils import full_name, all_func_args, find_key_case_insensitive, failure, get_logger


LOGGER = get_logger(__name__)


PARAM_LOG_MESSAGE = "Parameters: %s"
RESPONSE_LOG_MESSAGE = "Response: %s"
EXCEPTION_LOG_MESSAGE = "%s: %s in argument %s for path %s"
EXCEPTION_LOG_MESSAGE_PATHLESS = "%s: %s in argument %s"
ERROR_MESSAGE = "Error extracting parameters"
VALIDATE_ERROR_MESSAGE = "Error validating parameters. Errors: %s"
NON_SERIALIZABLE_ERROR_MESSAGE = "Response body is not JSON serializable"
CORS_INVALID_TYPE_ERROR = "Invalid value type in CORS header"
CORS_NON_DICT_ERROR = "Invalid response type for CORS headers"
CORS_INVALID_TYPE_LOG_MESSAGE = "Cannot set %s header to a non %s value"
CORS_NON_DICT_LOG_MESSAGE = "Cannot add headers to a non dictionary response"
UNKNOWN = "Unknown"


def extract_from_event(parameters, group_errors=False, allow_none_defaults=False):
    """
    Extracts a set of parameters from the event dictionary in a lambda handler.

    The extracted parameters are added as kwargs to the handler function.

    Usage:
        @extract_from_event([Parameter(path="/body[json]/my_param")])
        def lambda_handler(event, context, my_param=None)
            pass

    Args:
        parameters (list): A collection of Parameter type items.
        group_errors (bool): flag that indicates if error messages are to be grouped together
            (if set to False, validation will end on first error)
    """
    for param in parameters:
        param.func_param_name = "event"
    return extract(parameters, group_errors, allow_none_defaults)


def extract_from_context(parameters, group_errors=False, allow_none_defaults=False):
    """
    Extracts a set of parameters from the context dictionary in a lambda handler.

    The extracted parameters are added as kwargs to the handler function.

    Usage:
        @extract_from_context([Parameter(path="/parent/my_param")])
        def lambda_handler(event, context, my_param=None)
            pass

    Args:
        parameters (list): A collection of Parameter type items.
        group_errors (bool): flag that indicates if error messages are to be grouped together
            (if set to False, validation will end on first error)
    """
    for param in parameters:
        param.func_param_name = "context"
    return extract(parameters, group_errors, allow_none_defaults)


def extract(parameters, group_errors=False, allow_none_defaults=False):
    """
    Extracts a set of parameters from any function parameter passed to an AWS lambda handler.

    The extracted parameters are added as kwargs to the handler function.

    Usage:
        @extract([Parameter(path="headers/Authorization[jwt]/sub", var_name="user_id", func_param_name="event")])
        def lambda_handler(event, context, user_id=None)
            pass

    Args:
        parameters (list): A collection of Parameter type items.
        group_errors (bool): flag that indicates if error messages are to be grouped together
            (if set to False, validation will end on first error)
        allow_none_defaults: A flag to allow None defaults. If True, None defaults will be passed into the kwargs.
            If the flag is set to False, the None defaults will not be added to kwargs, and the default will be
            picked up (if exists) from the method signature.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                param = None
                errors = []
                arg_dictionary = all_func_args(func, args, kwargs)
                for param in parameters:
                    param_val = arg_dictionary[param.func_param_name]
                    return_val = param.extract_value(param_val)
                    param_errors = param.validate_path(return_val, group_errors)
                    if param_errors:
                        errors.append(param_errors)
                        if not group_errors:
                            LOGGER.error(VALIDATE_ERROR_MESSAGE, errors)
                            return failure(errors)
                    elif allow_none_defaults or return_val is not None:
                        kwargs[param.get_var_name()] = return_val
            except Exception as ex:  # noqa: pylint - broad-except
                LOGGER.error(EXCEPTION_LOG_MESSAGE, full_name(ex), str(ex),
                             param.func_param_name if param else UNKNOWN,
                             param.path if param else UNKNOWN)
                return failure(ERROR_MESSAGE)
            else:
                if group_errors and errors:
                    LOGGER.error(VALIDATE_ERROR_MESSAGE, errors)
                    return failure(errors)

                return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_exceptions(handlers):
    """
    Handles exceptions thrown by the wrapped/decorated function.

    Usage:
        @handle_exceptions([ExceptionHandler(exception=KeyError, friendly_message="Your message on KeyError except")]).
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
                failed_handler = [handler for handler in handlers if handler.exception is type(ex)][0]
                message = failed_handler.friendly_message

                if message and str(ex):
                    LOGGER.error("%s: %s", message, str(ex))
                else:
                    LOGGER.error(message if message else str(ex))

                return failure(message if message else str(ex), failed_handler.status_code)
        return wrapper
    return decorator


def log(parameters=False, response=False):
    """
    Log parameters and/or response of the wrapped/decorated function using logging package

    Args:
        parameters: a flag indicating if the input parameters are to be logged
        response: a flag indicating if the returned response is to be logged
    """
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
        @extract_from_ssm([SSMParameter(ssm_name="key", var_name="var")])
        def lambda_handler(var=None)
            pass

    Args:
        ssm_parameters (list): A collection of SSMParameter type items.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            ssm = boto3.client("ssm")
            server_key_containers = ssm.get_parameters(
                Names=[ssm_parameter.get_ssm_name() for ssm_parameter in ssm_parameters],
                WithDecryption=True)
            for key_container in server_key_containers["Parameters"]:
                for ssm_parameter in ssm_parameters:  # pragma: no cover
                    if ssm_parameter.get_ssm_name() == key_container["Name"]:
                        kwargs[ssm_parameter.get_var_name()] = key_container["Value"]
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
            return {"statusCode": 200, "body": {"key": "value"}}

        will return {"statusCode": 200, "body": "{"key":"value"}"}
    """
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if "body" in response:
            try:
                response["body"] = json.dumps(response["body"])
            except TypeError:
                return failure(NON_SERIALIZABLE_ERROR_MESSAGE, 500)
        return response
    return wrapper


def validate(parameters, group_errors=False):
    """
    Validates a set of function parameters.

    Usage:
        @validate([ValidatedParameter(func_param_name="my_param", validators=[...])])
        def func(my_param)
            pass

    Args:
        parameters (list): A collection of ValidatedParameter type items.
        group_errors (bool): flag that indicates if error messages are to be grouped together
            (if set to False, validation will end on first error)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                errors = []
                arg_dictionary = all_func_args(func, args, kwargs)
                for param in parameters:
                    param_val = arg_dictionary[param.func_param_name]
                    param_errors = param.validate(param_val, group_errors)
                    if param_errors:
                        errors.append({param.func_param_name: param_errors})
                        if not group_errors:
                            LOGGER.error(VALIDATE_ERROR_MESSAGE, errors)
                            return failure(errors)
            except Exception as ex:  # noqa: pylint - broad-except
                LOGGER.error(EXCEPTION_LOG_MESSAGE_PATHLESS, full_name(ex), str(ex), param.func_param_name)
                return failure(ERROR_MESSAGE)

            if group_errors and errors:
                LOGGER.error(VALIDATE_ERROR_MESSAGE, errors)
                return failure(errors)

            return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_all_exceptions():
    """
    Handles all exceptions thrown by the wrapped/decorated function.

    Usage:
        @handle_all_exceptions()
        def lambda_handler(params)
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:  # noqa: pylint - catching-non-exception
                LOGGER.error(str(ex))
                return failure(str(ex))
        return wrapper
    return decorator


def cors(allow_origin=None, allow_methods=None, allow_headers=None, max_age=None):
    """
    Adds CORS headers to the response of the decorated function

    Usage:
        @cors(allow_origin="http://example.com", allow_methods="POST,GET", allow_headers="Content-Type", max_age=86400)
        def func(my_param)
            pass

    Args:
        allow_origin: A string containing the comma-separated list of allowed origins
        allow_methods: A string containing the comma-separated list of allowed methods
        allow_headers: A string containing the comma-separated list of allowed headers
        max_age: An integer to indicate the caching time (in seconds) for the CORS pre-flight request

    Returns:
        The original decorated function response with the additional cors headers
    """
    def decorator(func):
        def wrapper(*args, **kwargs):

            def update_header(headers, header_name, value, value_type):
                if value:
                    if isinstance(value, value_type):
                        header_key = find_key_case_insensitive(header_name, headers)
                        headers[header_key] = f"{headers[header_key]},{value}" if header_key in headers else value
                    else:
                        LOGGER.error(CORS_INVALID_TYPE_LOG_MESSAGE, header_name, value_type)
                        raise TypeError

                return headers

            response = func(*args, **kwargs)

            if isinstance(response, dict):
                headers_key = find_key_case_insensitive("headers", response)

                resp_headers = response[headers_key] if headers_key in response else {}

                try:
                    resp_headers = update_header(resp_headers, "access-control-allow-origin", allow_origin, str)
                    resp_headers = update_header(resp_headers, "access-control-allow-methods", allow_methods, str)
                    resp_headers = update_header(resp_headers, "access-control-allow-headers", allow_headers, str)
                    resp_headers = update_header(resp_headers, "access-control-max-age", max_age, int)

                    response[headers_key] = resp_headers
                    return response
                except TypeError:
                    return failure(CORS_INVALID_TYPE_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                LOGGER.error(CORS_NON_DICT_LOG_MESSAGE)
                return failure(CORS_NON_DICT_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        return wrapper
    return decorator
