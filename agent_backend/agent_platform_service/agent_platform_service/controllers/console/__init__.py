from flask import Blueprint

from agent_platform_basic.libs.external_api import ExternalAPI
from fastapi import APIRouter

from .files import FileApi, FilePreviewApi, FileSupportTypeApi

console_api = APIRouter()
bp = Blueprint('console', __name__, url_prefix='/console/api')
api = ExternalAPI(bp)
api.add_resource(FileApi, "/files/upload")
api.add_resource(FilePreviewApi, "/files/<uuid:file_id>/preview")
api.add_resource(FileSupportTypeApi, "/files/support-type")
# Import other controllers
from . import admin, apikey, extension, feature, ping, setup, version

# Import app controllers
from .app import (
    advanced_prompt_template,
    agent,
    annotation,
    app,
    audio,
    completion,
    conversation,
    generator,
    message,
    model_config,
    ops_trace,
    site,
    statistic,
    workflow,
    workflow_app_log,
    workflow_run,
    workflow_statistic,
    create_code_tool,
    rag,
    agent_log,
    es,
    subscribe
)
# Import audit controllers
from .audit import application_audit

# Import auth controllers
from .auth import data_source_bearer_auth, login, oauth,user_permissions, create_account_and_tenant

# Import api controllers
#
# Import datasets controllers
from .datasets import data_source, datasets, datasets_document, datasets_segments, hit_testing

# Import explore controllers
from .explore import (
    audio,
    completion,
    conversation,
    installed_app,
    message,
    parameter,
    recommended_app,
    saved_message,
    workflow,
)

# Import tag controllers
from .tag import tags

# Import workspace controllers
from .workspace import account, load_balancing_config, members, model_providers, models, tool_providers, workspace, plugin

from .api import api_info