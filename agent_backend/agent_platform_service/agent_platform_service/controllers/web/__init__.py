from flask import Blueprint

from agent_platform_basic.libs.external_api import ExternalAPI
from fastapi import APIRouter

web_api = APIRouter()

bp = Blueprint('web', __name__, url_prefix='/api')
api = ExternalAPI(bp)

from . import app, audio, completion, conversation, feature, file, message, passport, saved_message, site, workflow
