from fastapi import APIRouter
from flask import Blueprint
from agent_platform_basic.libs.external_api import ExternalAPI

interface_api = APIRouter()

bp = Blueprint('interface_api', __name__, url_prefix='/interface/api')
api = ExternalAPI(bp)

from .tool_chain import statistics, model_notification
from .workflow_api import model_registration_passthrough
