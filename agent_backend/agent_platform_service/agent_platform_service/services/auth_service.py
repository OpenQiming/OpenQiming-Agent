from fastapi import Request, WebSocket, HTTPException
import logging
from agent_platform_basic.exceptions.base_http_exception import Unauthorized
from agent_platform_basic.extensions.ext_redis import async_redis_client
from agent_platform_basic.libs.helper import get_fastapi_remote_ip
from agent_platform_basic.libs.passport import PassportService
from agent_platform_common.configs import agent_platform_config
from agent_platform_service.services.account_service import AccountService


async def login_user(request: Request = None,
                     websocket: WebSocket = None):
    """Load user based on the request."""
    # if request.blueprint not in ['console', 'inner_api']:
    #     return None
    # Check if the user_id contains a dot, indicating the old format
    if request is not None:
        request_or_ws = request
    elif websocket is not None:
        request_or_ws = websocket
    else:
        raise HTTPException(status_code=400, detail="Neither request nor websocket provided")
    auth_header = request_or_ws.headers.get('Authorization', None)
    auth_token_with_schema = None
    if not auth_header:
        # 自有token校验逻辑
        auth_token_with_schema = request_or_ws.query_params.get('_token')
        if not auth_token_with_schema:
            raise Unauthorized("Authorization header missing")

    remote_ip = get_fastapi_remote_ip(request=request, websocket=websocket)

    auth_info = auth_header or auth_token_with_schema
    if auth_info and ' ' not in auth_info:
        # 启明单点逻辑
        return await AccountService.async_qiming_sso(auth_info, ip_address=remote_ip)
    else:
        # 自有token校验逻辑
        auth_scheme, auth_token = auth_info.split(None, 1)

        # 校验前缀
        auth_scheme = auth_scheme.lower()
        if auth_scheme != 'bearer':
            raise Unauthorized("Invalid Authorization header format. Expected \'Bearer <api-key>\' format.")

        # 是否登出
        token_black_list_key = f"agent_platform_account_token_black_list: {auth_token}"
        in_black_list = await async_redis_client.get(token_black_list_key)
        if in_black_list:
            raise Unauthorized('Invalid Authorization token.')

        decoded = PassportService(agent_platform_config).verify(auth_token)
        user_id = decoded.get('user_id')

        return await AccountService.async_load_user(user_id=user_id)
