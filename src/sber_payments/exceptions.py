import json


class ApiError(Exception):
    """Represents an exception returned by the remote API."""
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code

    def __str__(self):
        if isinstance(self.message, str):
            return self.message
        else:
            return json.dumps(self.message)


class SberAcquiringException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code


class ActionException(SberAcquiringException):
    pass


class BadCredentialsException(SberAcquiringException):
    pass


class BadRequestException(SberAcquiringException):
    pass


class BadResponseException(SberAcquiringException):
    pass


class NetworkException(SberAcquiringException):
    pass


class InvalidRequestArguments(SberAcquiringException):
    pass
