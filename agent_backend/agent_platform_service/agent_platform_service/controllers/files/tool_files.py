from flask import Response
from flask_restful import Resource, reqparse
from werkzeug.exceptions import Forbidden, NotFound

from agent_platform_basic.exceptions.base_http_exception import BaseHTTPException
from agent_platform_core.tools.tool_file_manager import ToolFileManager
from agent_platform_service.controllers.files import api


class ToolFilePreviewApi(Resource):
    def get(self, file_id, extension):
        file_id = str(file_id)

        parser = reqparse.RequestParser()

        parser.add_argument('timestamp', type=str, required=True, location='args')
        parser.add_argument('nonce', type=str, required=True, location='args')
        parser.add_argument('sign', type=str, required=True, location='args')

        args = parser.parse_args()

        if not ToolFileManager.verify_file(file_id=file_id,
                                            timestamp=args['timestamp'],
                                            nonce=args['nonce'],
                                            sign=args['sign'],
        ):
            raise Forbidden('Invalid request.')
        
        try:
            result = ToolFileManager.get_file_generator_by_tool_file_id(
                file_id,
            )

            if not result:
                raise NotFound('file is not found')
            
            generator, mimetype = result
        except Exception:
            raise UnsupportedFileTypeError()

        return Response(generator, mimetype=mimetype)

api.add_resource(ToolFilePreviewApi, '/files/tools/<uuid:file_id>.<string:extension>')

class UnsupportedFileTypeError(BaseHTTPException):
    error_code = 'unsupported_file_type'
    description = "File type not allowed."
    code = 415
