from agent_platform_basic.libs.login import current_user
from flask import request
from flask_restful import Resource, marshal_with

from agent_platform_service.controllers.common.errors import FilenameNotExistsError
from agent_platform_service.controllers.console.wraps import cloud_edition_billing_resource_check
from agent_platform_service.controllers.service_api import api
from agent_platform_basic.exceptions.controllers.service_api.app import (
    FileTooLargeError,
    NoFileUploadedError,
    TooManyFilesError,
    UnsupportedFileTypeError,
)
from agent_platform_service.controllers.service_api.wraps import FetchUserArg, WhereisUserArg, validate_app_token
from agent_platform_service.fields.file_fields import file_fields
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_service.services.file_service import FileService
import agent_platform_basic.exceptions.services as ServiceExceptions
from agent_platform_basic.exceptions.services.file import FileTooLargeError as ServiceFileTooLargeError
from agent_platform_basic.exceptions.services.file import UnsupportedFileTypeError as ServiceUnsupportedFileTypeError

class FileApi(Resource):

    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.FORM))
    @marshal_with(file_fields)
    def post(self, app_model: App, end_user: EndUser):

        file = request.files['file']
        tenant_id = request.form.get('tenant_id')

        # check file
        if 'file' not in request.files:
            raise NoFileUploadedError()

        if not file.mimetype:
            raise UnsupportedFileTypeError()

        if len(request.files) > 1:
            raise TooManyFilesError()

        try:
            upload_file = FileService.upload_file(file, end_user, tenant_id)
        except ServiceExceptions.file.FileTooLargeError as file_too_large_error:
            raise FileTooLargeError(file_too_large_error.description)
        except ServiceExceptions.file.UnsupportedFileTypeError:
            raise UnsupportedFileTypeError()

        return upload_file, 201


class ExternalFileApi(Resource):
    # @setup_required
    @marshal_with(file_fields)
    def post(self):
        file = request.files["file"]
        source = request.form.get("source")
        app_id = request.form.get("app_id")

        if "file" not in request.files:
            raise NoFileUploadedError()

        if len(request.files) > 1:
            raise TooManyFilesError()

        if not file.filename:
            raise FilenameNotExistsError

        if source not in ("datasets", None):
            source = None

        try:
            upload_file = FileService.upload_file(
                filename=file.filename,
                content=file.read(),
                mimetype=file.mimetype,
                user=None,
                source=source,
                app_id=app_id
            )
        except ServiceFileTooLargeError as file_too_large_error:
            raise FileTooLargeError(file_too_large_error.description)
        except ServiceUnsupportedFileTypeError:
            raise UnsupportedFileTypeError()

        return upload_file, 201

api.add_resource(FileApi, '/files/upload')
api.add_resource(ExternalFileApi, '/external/files/upload')
