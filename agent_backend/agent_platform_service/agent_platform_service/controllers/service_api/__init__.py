from flask import Blueprint
from fastapi import APIRouter
from agent_platform_basic.libs.external_api import ExternalAPI


service_api = APIRouter()
bp = Blueprint('service_api', __name__, url_prefix='/v1')
api = ExternalAPI(bp)



from . import index
from .app import app, audio, completion, conversation, file, message, workflow
from .dataset import dataset, document, segment
