import os

from starlette.responses import JSONResponse
from fastapi import Request

from agent_platform_basic.extensions.ext_redis import redis_client
from agent_platform_common.configs import agent_platform_config
#
# if not os.environ.get("DEBUG") or os.environ.get("DEBUG", "false").lower() != 'true':
#     # from gevent import monkey
#
#     # monkey.patch_all()
#
#     import grpc.experimental.gevent
#
#     grpc.experimental.gevent.init_gevent()

import json
import logging
import sys
import threading
import time
import warnings
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, Response, request
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized

from agent_platform_common.constants.metabolic_redis_const import METABOLIC_MESSAGE_REDIS_TIMEOUT, \
    MESSAGE_FROM_WORKFLOW_PREFIX

# DO NOT REMOVE BELOW
from agent_platform_service.events import event_handlers
from agent_platform_basic.extensions import (
    ext_compress,
    ext_database,
    ext_login,
    ext_mail,
    ext_migrate,
    ext_redis,
    ext_sentry,
    ext_storage,
)
from agent_platform_service.extensions import ext_celery
from agent_platform_core.extension import ext_code_based_extension, ext_hosting_provider
from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.extensions.ext_login import login_manager
from agent_platform_basic.libs.passport import PassportService
from .services.account_service import AccountService

# DO NOT REMOVE ABOVE


warnings.simplefilter("ignore", ResourceWarning)

# fix windows platform
if os.name == "nt":
    os.system('tzutil /s "China Standard Time"')
else:
    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()


class AgentPlatformApp(Flask):
    pass


# -------------
# Configuration
# -------------


config_type = os.getenv('EDITION', default='SELF_HOSTED')  # ce edition first


# ----------------------------
# Application Factory Function
# ----------------------------

def create_flask_app_with_configs() -> Flask:
    """
    create a raw flask app
    with configs loaded from .env file
    """
    agent_platform_app = AgentPlatformApp(__name__)
    agent_platform_app.config.from_mapping(agent_platform_config.model_dump())

    # populate configs into system environment variables
    for key, value in agent_platform_app.config.items():
        if isinstance(value, str):
            os.environ[key] = value
        elif isinstance(value, int | float | bool):
            os.environ[key] = str(value)
        elif value is None:
            os.environ[key] = ''

    return agent_platform_app


def create_fastapi_app_with_configs() -> FastAPI:
    """
    create a raw flask app
    with configs loaded from .env file
    """
    agent_platform_app = FastAPI()
    agent_platform_app.state.config = agent_platform_config.model_dump()

    # populate configs into system environment variables
    for key, value in agent_platform_app.state.config.items():
        if isinstance(value, str):
            os.environ[key] = value
        elif isinstance(value, int | float | bool):
            os.environ[key] = str(value)
        elif value is None:
            os.environ[key] = ''
    return agent_platform_app


def create_app() -> Flask:
    app = create_flask_app_with_configs()

    app.secret_key = app.config['SECRET_KEY']

    log_handlers = None
    log_file = app.config.get('LOG_FILE')
    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers = [
            RotatingFileHandler(
                filename=log_file,
                maxBytes=1024 * 1024 * 1024,
                backupCount=5
            ),
            logging.StreamHandler(sys.stdout)
        ]

    logging.basicConfig(
        level=app.config.get('LOG_LEVEL'),
        format=app.config.get('LOG_FORMAT'),
        datefmt=app.config.get('LOG_DATEFORMAT'),
        handlers=log_handlers,
        force=True
    )
    log_tz = app.config.get('LOG_TZ')
    if log_tz:
        from datetime import datetime

        import pytz
        timezone = pytz.timezone(log_tz)

        def time_converter(seconds):
            return datetime.utcfromtimestamp(seconds).astimezone(timezone).timetuple()

        for handler in logging.root.handlers:
            handler.formatter.converter = time_converter
    initialize_extensions(app)
    register_blueprints(app)

    return app


def create_fastapi_app() -> FastAPI:
    log_handlers = None
    log_file = agent_platform_config.LOG_FILE
    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers = [
            RotatingFileHandler(
                filename=log_file,
                maxBytes=1024 * 1024 * 1024,
                backupCount=5
            ),
            logging.StreamHandler(sys.stdout)
        ]
    logging.basicConfig(
        level=agent_platform_config.LOG_LEVEL,
        format=agent_platform_config.LOG_FORMAT,
        datefmt=agent_platform_config.LOG_DATEFORMAT,
        handlers=log_handlers,
        force=True
    )

    fastapi_app = create_fastapi_app_with_configs()
    ext_database.init_fastapi(fastapi_app)
    ext_redis.init_fastapi(fastapi_app)
    ext_storage.init_fastapi(fastapi_app)
    register_apirouter_fastapi(fastapi_app)
    return fastapi_app


def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    ext_compress.init_app(app)
    ext_code_based_extension.init()
    ext_database.init_app(app)
    ext_migrate.init(app, db)
    ext_redis.init_app(app)
    ext_storage.init_app(app)
    # ext_celery.init_app(app)
    ext_login.init_app(app)
    ext_mail.init_app(app)
    ext_hosting_provider.init_app(app)
    ext_sentry.init_app(app)


# Flask-Login configuration
@login_manager.request_loader
def load_user_from_request(request_from_flask_login):
    """Load user based on the request."""
    if request.blueprint not in ['console', 'inner_api']:
        return None
    # Check if the user_id contains a dot, indicating the old format
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        # 自有token校验逻辑
        auth_token = request.args.get('_token')
        if not auth_token:
            raise Unauthorized('Invalid Authorization token.')

        # 是否登出
        token_black_list_key = f"agent_platform_account_token_black_list: {auth_token}"
        if redis_client.get(token_black_list_key):
            raise Unauthorized('Invalid Authorization token.')

        decoded = PassportService(agent_platform_config).verify(auth_token)
        user_id = decoded.get('user_id')

        return AccountService.load_user(user_id=user_id)

    else:
        if ' ' not in auth_header:
            # 启明单点逻辑
            return AccountService.qiming_sso(auth_header)
        else:
            # 自有token校验逻辑
            auth_scheme, auth_token = auth_header.split(None, 1)
            auth_scheme = auth_scheme.lower()

            # 校验前缀
            if auth_scheme != 'bearer':
                raise Unauthorized('Invalid Authorization header format. Expected \'Bearer <api-key>\' format.')

            # 是否登出
            token_black_list_key = f"agent_platform_account_token_black_list: {auth_header}"
            if redis_client.get(token_black_list_key):
                raise Unauthorized('Invalid Authorization token.')

            decoded = PassportService(agent_platform_config).verify(auth_token)
            user_id = decoded.get('user_id')

            return AccountService.load_user(user_id=user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    """Handle unauthorized requests."""
    return Response(json.dumps({
        'code': 'unauthorized',
        'message': "Unauthorized."
    }), status=401, content_type="application/json")


def register_apirouter_fastapi(fastapi_app):
    from agent_platform_service.controllers.console import console_api
    from agent_platform_service.controllers.inner_api import inner_api
    from agent_platform_service.controllers.web import web_api
    from agent_platform_service.controllers.service_api import service_api
    from agent_platform_service.controllers.interface import interface_api
    from agent_platform_basic.middlewares.cors_middleware import PathBasedCORSMiddleware

    global_prefix = fastapi_app.state.config.get("GLOBAL_APIROUTER_PREFIX")
    inner_api_path = f"{global_prefix}/inner/api"
    web_api_path = f"{global_prefix}/api"
    console_api_path = f"{global_prefix}/console/api"
    service_api_path = f"{global_prefix}/v1"
    interface_api_path = f"{global_prefix}/interface/api"
    fastapi_app.include_router(inner_api, prefix=inner_api_path, tags=[inner_api_path])
    fastapi_app.include_router(web_api, prefix=web_api_path, tags=[web_api_path])
    fastapi_app.include_router(console_api, prefix=console_api_path, tags=[console_api_path])
    fastapi_app.include_router(service_api, prefix=service_api_path, tags=[service_api_path])
    fastapi_app.include_router(interface_api, prefix=interface_api_path, tags=[interface_api_path])

    path_cors_config = {
        web_api_path: {
            "Access-Control-Allow-Origin": fastapi_app.state.config['WEB_API_CORS_ALLOW_ORIGINS'],
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,OPTIONS,PATCH",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-App-Code",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "X-Version,X-Env"
        },
        console_api_path: {
            "Access-Control-Allow-Origin": fastapi_app.state.config['CONSOLE_CORS_ALLOW_ORIGINS'],
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,OPTIONS,PATCH",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "X-Version,X-Env"
        },
        interface_api_path: {
            "Access-Control-Allow-Origin": fastapi_app.state.config['CONSOLE_CORS_ALLOW_ORIGINS'],
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,OPTIONS,PATCH",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "X-Version,X-Env"
        }
    }
    fastapi_app.add_middleware(PathBasedCORSMiddleware, path_cors_config=path_cors_config)


# register blueprint routers
def register_blueprints(app):
    from agent_platform_service.controllers.console import bp as console_app_bp
    from agent_platform_service.controllers.files import bp as files_bp
    from agent_platform_service.controllers.inner_api import bp as inner_api_bp
    from agent_platform_service.controllers.service_api import bp as service_api_bp
    from agent_platform_service.controllers.web import bp as web_bp
    from agent_platform_service.controllers.interface import bp as interface_bp

    CORS(service_api_bp,
         allow_headers=['Content-Type', 'Authorization', 'X-App-Code'],
         methods=['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'PATCH']
         )
    app.register_blueprint(service_api_bp)

    CORS(web_bp,
         resources={
             r"/*": {"origins": app.config['WEB_API_CORS_ALLOW_ORIGINS']}},
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-App-Code'],
         methods=['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'PATCH'],
         expose_headers=['X-Version', 'X-Env']
         )

    app.register_blueprint(web_bp)

    CORS(console_app_bp,
         resources={
             r"/*": {"origins": app.config['CONSOLE_CORS_ALLOW_ORIGINS']}},
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'PATCH'],
         expose_headers=['X-Version', 'X-Env']
         )

    app.register_blueprint(console_app_bp)

    CORS(files_bp,
         allow_headers=['Content-Type'],
         methods=['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'PATCH']
         )
    app.register_blueprint(files_bp)

    app.register_blueprint(inner_api_bp)

    app.register_blueprint(interface_bp)


# create app
app = create_app()
fastapi_app = create_fastapi_app()
celery = ext_celery.init_app(app)

if app.config.get('TESTING'):
    print("App is running in TESTING mode")


@app.after_request
def after_request(response):
    """Add Version headers to the response."""
    response.set_cookie('remember_token', '', expires=0)
    response.headers.add('X-Version', app.config['CURRENT_VERSION'])
    response.headers.add('X-Env', app.config['DEPLOY_ENV'])
    return response


@app.route('/flask-health')
def health():
    return Response(json.dumps({
        "msg": "操作成功",
        "code": 200,
        "data": [
            {
                "province_tag": "hq,hq",
                "scene_tag": "xczc_xczhw",
                "specialty_tag": "jrw_zhw"
            }
        ]
    }, ensure_ascii=False), status=200, content_type="application/json")


@fastapi_app.get('/health')
async def fastapi_health():
    return {
        "msg": "操作成功",
        "code": 200,
        "data": [
            {
                "province_tag": "hq,hq",
                "scene_tag": "xczc_xczhw",
                "specialty_tag": "jrw_zhw"
            }
        ]
    }


@app.route('/healthMetabolic')
def healthMetabolic():
    import asyncio

    from agent_platform_metabolic.context import Context
    from agent_platform_metabolic.hand_made_agents.roles.account_agent import AccountAgent
    from agent_platform_metabolic.logs import logger
    async def main():
        msg = "Write a PRD for a snake game"
        context = Context()  # 显式创建会话Context对象，Role对象会隐式的自动将它共享给自己的Action对象
        role = AccountAgent()
        context.llm()
        while msg:
            msg = await role.run(msg)
            logger.info(str(msg))

    asyncio.run(main())
    return Response(json.dumps({
        'status': 'ok',
        'version': app.config['CURRENT_VERSION']
    }), status=200, content_type="application/json")


@fastapi_app.get('/healthMetabolicFastAPI')
async def healthMetabolicFastAPI():
    from agent_platform_metabolic.hand_made_agents.envs.metabolic_env import MetabolicEnv
    from agent_platform_metabolic.hand_made_agents.roles.account_agent import AccountAgent
    from agent_platform_metabolic.hand_made_agents.roles.fault_report_agent import FaultReportAgent
    from agent_platform_metabolic.hand_made_agents.roles.sigma_agent import SigmaAgent
    from agent_platform_basic.extensions.ext_redis import redis_client
    from agent_platform_metabolic.schema import Message
    from agent_platform_metabolic.hand_made_agents.actions.workflow_actions import AccountInput

    user_id = "abc123"
    workflow_id = "cde789"

    msg = Message(content="[\"abc11251245\",\"ads61325213\",\"vas15311111\",\"gak96130510\",\"dad05124051\"]",
                  cause_by=AccountInput,
                  send_to="AccountAgent")

    redis_client.set(f"{MESSAGE_FROM_WORKFLOW_PREFIX}:abc123_cde789",
                     msg.dump(), ex=METABOLIC_MESSAGE_REDIS_TIMEOUT)

    env = MetabolicEnv(user_id=user_id, workflow_id=workflow_id)

    env.add_roles([SigmaAgent(), AccountAgent(), FaultReportAgent()])
    await env.run()


@app.route('/threads')
def threads():
    num_threads = threading.active_count()
    threads = threading.enumerate()

    thread_list = []
    for thread in threads:
        thread_name = thread.name
        thread_id = thread.ident
        is_alive = thread.is_alive()

        thread_list.append({
            'name': thread_name,
            'id': thread_id,
            'is_alive': is_alive
        })

    return {
        'thread_num': num_threads,
        'threads': thread_list
    }


@app.route('/db-pool-stat')
def pool_stat():
    engine = db.engine
    return {
        'pool_size': engine.pool.size(),
        'checked_in_connections': engine.pool.checkedin(),
        'checked_out_connections': engine.pool.checkedout(),
        'overflow_connections': engine.pool.overflow(),
        'connection_timeout': engine.pool.timeout(),
        'recycle_time': db.engine.pool._recycle
    }


fastapi_app.mount(agent_platform_config.GLOBAL_APIROUTER_PREFIX or '/', WSGIMiddleware(app))


@fastapi_app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"{exc}"}
    )


if __name__ == '__main__':
    import uvicorn

    # 开发
    uvicorn.run(fastapi_app, host='0.0.0.0', port=5001, workers=1)

    # 生产启动命令
    # uvicorn app:fastapi_app --host 0.0.0.0 --port 5001 --workers 4 --loop uvloop
