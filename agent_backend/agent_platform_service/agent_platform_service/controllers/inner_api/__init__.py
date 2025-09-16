from flask import Blueprint

from agent_platform_basic.libs.external_api import ExternalAPI
from fastapi import APIRouter

inner_api = APIRouter()

bp = Blueprint('inner_api', __name__, url_prefix='/inner/api')
api = ExternalAPI(bp)

from .workspace import workspace
