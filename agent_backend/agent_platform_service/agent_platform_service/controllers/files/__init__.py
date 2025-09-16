from flask import Blueprint

from agent_platform_basic.libs.external_api import ExternalAPI

bp = Blueprint('files', __name__)
api = ExternalAPI(bp)


from . import image_preview, tool_files
