from flask import request
from flask_restful import marshal_with

import agent_platform_basic.exceptions.services as ServiceExceptions
from agent_platform_basic.exceptions.controllers.web import FileTooLargeError, NoFileUploadedError, TooManyFilesError, \
    UnsupportedFileTypeError
from agent_platform_service.controllers.web import api
from agent_platform_service.controllers.web.wraps import WebApiResource
from agent_platform_service.fields.file_fields import file_fields
from agent_platform_service.services.file_service import FileService


class FileApi(WebApiResource):

    @marshal_with(file_fields)
    def post(self, app_model, end_user):
        # get file from request
        file = request.files['file']

        # check file
        if 'file' not in request.files:
            raise NoFileUploadedError()

        if len(request.files) > 1:
            raise TooManyFilesError()
        try:
            upload_file = FileService.upload_file(file, end_user)
        except ServiceExceptions.file.FileTooLargeError as file_too_large_error:
            raise FileTooLargeError(file_too_large_error.description)
        except ServiceExceptions.file.UnsupportedFileTypeError:
            raise UnsupportedFileTypeError()

        return upload_file, 201


api.add_resource(FileApi, '/files/upload')
