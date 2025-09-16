from typing import Optional

from fastapi import HTTPException as FastAPIHTTPException
from werkzeug.exceptions import (
    HTTPException as WerkzeugHTTPException,
    Unauthorized as WerkzeugUnauthorized,
    Forbidden as WerkzeugForbidden,
    InternalServerError as WerkzeugInternalServerError,
    NotFound as WerkzeugNotFound,
)

""" 
@Date    ：2024/7/8 15:31 
@Version: 1.0
@Description:
    BaseHTTPException
"""


class BaseHTTPException(FastAPIHTTPException, WerkzeugHTTPException):
    code: str = 400
    description: str = None

    def __init__(self, detail: str = description, headers: dict = None, response=None):
        detail = detail or self.description
        # FastAPI HTTPException requires status_code and detail
        FastAPIHTTPException.__init__(self, status_code=self.code, detail=detail, headers=headers)
        # Werkzeug HTTPException requires a description
        WerkzeugHTTPException.__init__(self, description=detail, response=response)


class Unauthorized(FastAPIHTTPException, WerkzeugUnauthorized):

    code = 401
    description = (
        "The server could not verify that you are authorized to access"
        " the URL requested. You either supplied the wrong credentials"
        " (e.g. a bad password), or your browser doesn't understand"
        " how to supply the credentials required."
    )

    def __init__(self, detail: str = description, headers: dict = None, response=None, www_authenticate=None):
        detail = detail or self.description
        # FastAPI HTTPException requires status_code and detail
        FastAPIHTTPException.__init__(self, status_code=self.code, detail=detail, headers=headers)
        # Werkzeug HTTPException requires a description
        WerkzeugUnauthorized.__init__(self, description=detail, response=response, www_authenticate=www_authenticate)


class Forbidden(FastAPIHTTPException, WerkzeugForbidden):

    code = 403
    description = (
        "You don't have the permission to access the requested"
        " resource. It is either read-protected or not readable by the"
        " server."
    )

    def __init__(self, detail: str = description, headers: dict = None, response=None):
        detail = detail or self.description
        # FastAPI HTTPException requires status_code and detail
        FastAPIHTTPException.__init__(self, status_code=self.code, detail=detail, headers=headers)
        # Werkzeug HTTPException requires a description
        WerkzeugForbidden.__init__(self, description=detail, response=response)


class NotFound(FastAPIHTTPException, WerkzeugNotFound):

    code = 404
    description = (
        "The requested URL was not found on the server. If you entered"
        " the URL manually please check your spelling and try again."
    )

    def __init__(self, detail: str = description, code: int = code, headers: dict = None, response=None):
        detail = detail or self.description
        # FastAPI HTTPException requires status_code and detail
        FastAPIHTTPException.__init__(self, status_code=code, detail=detail, headers=headers)
        # Werkzeug HTTPException requires a description
        WerkzeugForbidden.__init__(self, description=detail, response=response)


class InternalServerError(FastAPIHTTPException, WerkzeugInternalServerError):

    code = 500
    description = (
        "The server encountered an internal error and was unable to"
        " complete your request. Either the server is overloaded or"
        " there is an error in the application."
    )

    def __init__(self, detail: str = description, headers: dict = None, response=None):
        detail = detail or self.description
        # FastAPI HTTPException requires status_code and detail
        FastAPIHTTPException.__init__(self, status_code=self.code, detail=detail, headers=headers)
        # Werkzeug HTTPException requires a description
        WerkzeugForbidden.__init__(self, description=detail, response=response)
