from datetime import datetime
from typing import Optional

import pytz
from fastapi import Depends, Query
from fastapi_pagination import Params
from flask_login import current_user
from flask_restful import Resource, marshal_with, reqparse
from flask_restful.inputs import int_range
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import Forbidden, NotFound, BadRequest
from fastapi_pagination.ext.sqlalchemy import paginate

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.libs.helper import datetime_string
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model import Account
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.models.db_model.model import Conversation, Message, MessageAnnotation, App
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.app.wraps import get_app_model, get_app_model_async
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.fastapi_fields.resp.console.conversation_resp import ConversationResp, \
    PaginateConversationResp
from agent_platform_service.fields.conversation_fields import (
    conversation_detail_fields,
    conversation_message_detail_fields,
    conversation_pagination_fields,
    conversation_with_summary_pagination_fields,
)
from agent_platform_service.fields.model_async.conversation_async import ConversationAsync
from agent_platform_service.services.auth_service import login_user


# @console_api.get("/apps/{app_id}/completion-conversations", response_model=PaginateConversationResp,
#                  summary="获取completion类型的所有对话", description="根据app_id获取completion类型的所有对话。",
#                  tags=["conversation"])
async def completion_conversation_api_get(app_id: str, keyword: Optional[str] = Query(None),
                                          start: Optional[str] = Query(None),
                                          end: Optional[str] = Query(None),
                                          annotation_status: Optional[str] = Query('all'),
                                          page: Optional[int] = Query(1, ge=1, le=99999),
                                          limit: Optional[int] = Query(20, ge=1, le=100),
                                          current_user: Account = Depends(login_user),
                                          session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                          conversation_async=Depends(ConversationAsync)
                                          ):
    if not current_user.is_editor:
        raise Forbidden()

    valid_annotation_status = {'annotated', 'not_annotated', 'all'}
    if annotation_status and annotation_status not in valid_annotation_status:
        raise BadRequest('Invalid annotation status')

    app_model = await get_app_model_async(app_id=app_id, mode=AppMode.COMPLETION)
    query = select(Conversation).where(Conversation.app_id == app_model.id, Conversation.mode == 'completion')

    if keyword:
        query = query.join(
            Message, Message.conversation_id == Conversation.id
        ).filter(
            or_(
                Message.query.ilike('%{}%'.format(keyword)),
                Message.answer.ilike('%{}%'.format(keyword))
            )
        )

    account = current_user
    timezone = pytz.timezone(account.timezone)
    utc_timezone = pytz.utc

    if start:
        start_datetime = datetime.strptime(start, '%Y-%m-%d %H:%M')
        start_datetime = start_datetime.replace(second=0)

        start_datetime_timezone = timezone.localize(start_datetime)
        start_datetime_utc = start_datetime_timezone.astimezone(utc_timezone)

        # 清除时区信息。postgres默认的timestamp字段类型是timestamp without time zone, 在同步调用时 Psycopg2 会把时区清除掉
        # 再比较，而异步调用时没有该逻辑，所以带有时区的数据是不能插入或进行比较的。除非将字段的类型 timestamp 改为 timestamptz
        query = query.where(Conversation.created_at >= start_datetime_utc.replace(tzinfo=None))

    if end:
        end_datetime = datetime.strptime(end, '%Y-%m-%d %H:%M')
        end_datetime = end_datetime.replace(second=59)

        end_datetime_timezone = timezone.localize(end_datetime)
        end_datetime_utc = end_datetime_timezone.astimezone(utc_timezone)

        # 清除时区信息。理由同上
        query = query.where(Conversation.created_at < end_datetime_utc.replace(tzinfo=None))

    if annotation_status == "annotated":
        query = query.options(joinedload(Conversation.message_annotations)).join(
            MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
        )
    elif annotation_status == "not_annotated":
        query = query.outerjoin(
            MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
        ).group_by(Conversation.id).having(func.count(MessageAnnotation.id) == 0)

    query = query.order_by(Conversation.created_at.desc())

    conversations = await paginate(session, query,
                                   Params(page=page, size=limit))

    ret_datas = list()
    for data in conversations.items:
        conversation_resp = await ConversationResp.to_conversation(data, conversation_async)
        ret_datas.append(conversation_resp)

    return PaginateConversationResp.get_result(ret_datas, conversations.total, page, limit)


class CompletionConversationApi(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=AppMode.COMPLETION)
    @marshal_with(conversation_pagination_fields)
    def get(self, app_model):
        if not current_user.is_editor:
            raise Forbidden()
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', type=str, location='args')
        parser.add_argument('start', type=datetime_string('%Y-%m-%d %H:%M'), location='args')
        parser.add_argument('end', type=datetime_string('%Y-%m-%d %H:%M'), location='args')
        parser.add_argument('annotation_status', type=str,
                            choices=['annotated', 'not_annotated', 'all'], default='all', location='args')
        parser.add_argument('page', type=int_range(1, 99999), default=1, location='args')
        parser.add_argument('limit', type=int_range(1, 100), default=20, location='args')
        args = parser.parse_args()

        query = db.select(Conversation).where(Conversation.app_id == app_model.id, Conversation.mode == 'completion')

        if args['keyword']:
            query = query.join(
                Message, Message.conversation_id == Conversation.id
            ).filter(
                or_(
                    Message.query.ilike('%{}%'.format(args['keyword'])),
                    Message.answer.ilike('%{}%'.format(args['keyword']))
                )
            )

        account = current_user
        timezone = pytz.timezone(account.timezone)
        utc_timezone = pytz.utc

        if args['start']:
            start_datetime = datetime.strptime(args['start'], '%Y-%m-%d %H:%M')
            start_datetime = start_datetime.replace(second=0)

            start_datetime_timezone = timezone.localize(start_datetime)
            start_datetime_utc = start_datetime_timezone.astimezone(utc_timezone)

            query = query.where(Conversation.created_at >= start_datetime_utc)

        if args['end']:
            end_datetime = datetime.strptime(args['end'], '%Y-%m-%d %H:%M')
            end_datetime = end_datetime.replace(second=59)

            end_datetime_timezone = timezone.localize(end_datetime)
            end_datetime_utc = end_datetime_timezone.astimezone(utc_timezone)

            query = query.where(Conversation.created_at < end_datetime_utc)

        if args['annotation_status'] == "annotated":
            query = query.options(joinedload(Conversation.message_annotations)).join(
                MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
            )
        elif args['annotation_status'] == "not_annotated":
            query = query.outerjoin(
                MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
            ).group_by(Conversation.id).having(func.count(MessageAnnotation.id) == 0)

        query = query.order_by(Conversation.created_at.desc())

        conversations = db.paginate(
            query,
            page=args['page'],
            per_page=args['limit'],
            error_out=False
        )

        return conversations


# @console_api.get('/apps/{app_id}/completion-conversations/{conversation_id}', response_model=ConversationResp,
#                  summary="获取completion类型的对话", description="根据app_id和conversation_id获取completion类型的对话。",
#                  tags=["conversation"])
async def completion_conversation_detail_api_get(app_id: str, conversation_id,
                                                 current_user: Account = Depends(login_user),
                                                 session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                                 conversation_async=Depends(ConversationAsync)):
    if not current_user.is_editor:
        raise Forbidden()
    conversation_id = str(conversation_id)
    app_model = await get_app_model_async(app_id=app_id, mode=AppMode.COMPLETION)
    conversation = await _get_conversation_async(app_model, conversation_id, current_user, session)
    return await ConversationResp.to_conversation_with_message_details(conversation, conversation_async)


# @console_api.delete('/apps/{app_id}/completion-conversations/{conversation_id}',
#                     summary="获取 completion 类型的对话",
#                     description="根据a pp_id 和 conversation_id 删除 completion 类型的对话。",
#                     tags=["conversation"])
async def completion_conversation_detail_api_delete(app_id: str, conversation_id,
                                                    current_user: Account = Depends(login_user),
                                                    session: AsyncSession = Depends(DbUtils.get_db_async_session)):
    if not current_user.is_editor:
        raise Forbidden()
    conversation_id = str(conversation_id)
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    conversation = await session.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.app_id == app_model.id))

    conversation = conversation.scalar_one_or_none()

    if not conversation:
        raise NotFound("Conversation Not Exists.")

    conversation.is_deleted = True
    await session.commit()

    return {'result': 'success'}, 204


class CompletionConversationDetailApi(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=AppMode.COMPLETION)
    @marshal_with(conversation_message_detail_fields)
    def get(self, app_model, conversation_id):
        if not current_user.is_editor:
            raise Forbidden()
        conversation_id = str(conversation_id)

        return _get_conversation(app_model, conversation_id)

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    def delete(self, app_model, conversation_id):
        if not current_user.is_editor:
            raise Forbidden()
        conversation_id = str(conversation_id)

        conversation = db.session.query(Conversation) \
            .filter(Conversation.id == conversation_id, Conversation.app_id == app_model.id).first()

        if not conversation:
            raise NotFound("Conversation Not Exists.")

        conversation.is_deleted = True
        db.session.commit()

        return {'result': 'success'}, 204


# @console_api.get('/apps/{app_id}/chat-conversations', response_model=PaginateConversationResp,
#                  summary="获取 chat 类型的所有对话", description="根据app_id获取 chat 类型的所有对话。",
#                  tags=["conversation"])
async def chat_conversation_api_get(app_id: str, keyword: Optional[str] = Query(None),
                                    start: Optional[str] = Query(None),
                                    end: Optional[str] = Query(None),
                                    annotation_status: Optional[str] = Query('all'),
                                    page: Optional[int] = Query(1, ge=1, le=99999),
                                    limit: Optional[int] = Query(20, ge=1, le=100),
                                    message_count_gte: Optional[int] = Query(1, ge=1, le=99999),
                                    current_user: Account = Depends(login_user),
                                    session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                    conversation_async=Depends(ConversationAsync)):
    if not current_user.is_editor:
        raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    query = db.select(Conversation).where(Conversation.app_id == app_model.id)

    if keyword:
        query = query.join(
            Message, Message.conversation_id == Conversation.id
        ).filter(
            or_(
                Message.query.ilike('%{}%'.format(keyword)),
                Message.answer.ilike('%{}%'.format(keyword)),
                Conversation.name.ilike('%{}%'.format(keyword)),
                Conversation.introduction.ilike('%{}%'.format(keyword)),
            ),

        )
    account = current_user
    timezone = pytz.timezone(account.timezone)
    utc_timezone = pytz.utc

    if start:
        start_datetime = datetime.strptime(start, '%Y-%m-%d %H:%M')
        start_datetime = start_datetime.replace(second=0)

        start_datetime_timezone = timezone.localize(start_datetime)
        start_datetime_utc = start_datetime_timezone.astimezone(utc_timezone)

        # 清除时区信息。postgres默认的timestamp字段类型是timestamp without time zone, 在同步调用时 Psycopg2 会把时区清除掉
        # 再比较，而异步调用时没有该逻辑，所以带有时区的数据是不能插入或进行比较的。除非将字段的类型 timestamp 改为 timestamptz
        query = query.where(Conversation.created_at >= start_datetime_utc.replace(tzinfo=None))

    if end:
        end_datetime = datetime.strptime(end, '%Y-%m-%d %H:%M')
        end_datetime = end_datetime.replace(second=59)

        end_datetime_timezone = timezone.localize(end_datetime)
        end_datetime_utc = end_datetime_timezone.astimezone(utc_timezone)

        # 清除时区信息。理由同上
        query = query.where(Conversation.created_at < end_datetime_utc.replace(tzinfo=None))

    if annotation_status == "annotated":
        query = query.options(joinedload(Conversation.message_annotations)).join(
            MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
        )
    if message_count_gte and message_count_gte >= 1:
        query = (
            query.options(joinedload(Conversation.messages))
            .join(Message, Message.conversation_id == Conversation.id)
            .group_by(Conversation.id)
            .having(func.count(Message.id) >= message_count_gte)
        )

    if app_model.mode == AppMode.ADVANCED_CHAT.value:
        query = query.where(Conversation.invoke_from != InvokeFrom.DEBUGGER.value)

    query = query.order_by(Conversation.created_at.desc())

    conversations = await paginate(session, query,
                                   Params(page=page, size=limit))

    ret_datas = list()

    for data in conversations.items:
        conversation_resp = await ConversationResp.to_conversation_with_summary(data, conversation_async)
        ret_datas.append(conversation_resp)

    return PaginateConversationResp.get_result(ret_datas, conversations.total, page, limit)


class ChatConversationApi(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    @marshal_with(conversation_with_summary_pagination_fields)
    def get(self, app_model):
        if not current_user.is_editor:
            raise Forbidden()
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', type=str, location='args')
        parser.add_argument('start', type=datetime_string('%Y-%m-%d %H:%M'), location='args')
        parser.add_argument('end', type=datetime_string('%Y-%m-%d %H:%M'), location='args')
        parser.add_argument('annotation_status', type=str,
                            choices=['annotated', 'not_annotated', 'all'], default='all', location='args')
        parser.add_argument('message_count_gte', type=int_range(1, 99999), required=False, location='args')
        parser.add_argument('page', type=int_range(1, 99999), required=False, default=1, location='args')
        parser.add_argument('limit', type=int_range(1, 100), required=False, default=20, location='args')
        args = parser.parse_args()

        query = db.select(Conversation).where(Conversation.app_id == app_model.id)

        if args['keyword']:
            query = query.join(
                Message, Message.conversation_id == Conversation.id
            ).filter(
                or_(
                    Message.query.ilike('%{}%'.format(args['keyword'])),
                    Message.answer.ilike('%{}%'.format(args['keyword'])),
                    Conversation.name.ilike('%{}%'.format(args['keyword'])),
                    Conversation.introduction.ilike('%{}%'.format(args['keyword'])),
                ),

            )

        account = current_user
        timezone = pytz.timezone(account.timezone)
        utc_timezone = pytz.utc

        if args['start']:
            start_datetime = datetime.strptime(args['start'], '%Y-%m-%d %H:%M')
            start_datetime = start_datetime.replace(second=0)

            start_datetime_timezone = timezone.localize(start_datetime)
            start_datetime_utc = start_datetime_timezone.astimezone(utc_timezone)

            query = query.where(Conversation.created_at >= start_datetime_utc)

        if args['end']:
            end_datetime = datetime.strptime(args['end'], '%Y-%m-%d %H:%M')
            end_datetime = end_datetime.replace(second=59)

            end_datetime_timezone = timezone.localize(end_datetime)
            end_datetime_utc = end_datetime_timezone.astimezone(utc_timezone)

            query = query.where(Conversation.created_at < end_datetime_utc)

        if args['annotation_status'] == "annotated":
            query = query.options(joinedload(Conversation.message_annotations)).join(
                MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
            )
        elif args['annotation_status'] == "not_annotated":
            query = query.outerjoin(
                MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
            ).group_by(Conversation.id).having(func.count(MessageAnnotation.id) == 0)

        if args['message_count_gte'] and args['message_count_gte'] >= 1:
            query = (
                query.options(joinedload(Conversation.messages))
                .join(Message, Message.conversation_id == Conversation.id)
                .group_by(Conversation.id)
                .having(func.count(Message.id) >= args['message_count_gte'])
            )

        if app_model.mode == AppMode.ADVANCED_CHAT.value:
            query = query.where(Conversation.invoke_from != InvokeFrom.DEBUGGER.value)

        query = query.order_by(Conversation.created_at.desc())

        conversations = db.paginate(
            query,
            page=args['page'],
            per_page=args['limit'],
            error_out=False
        )

        return conversations


# @console_api.get('/apps/{app_id}/chat-conversations/{conversation_id}', response_model=ConversationResp,
#                  summary="获取 chat 类型的单个对话", description="根据 app_id 和 conversation_id 获取 chat 类型的对话。",
#                  tags=["conversation"])
async def chat_conversation_detail_api_get(app_id: str, conversation_id: str,
                                           current_user: Account = Depends(login_user),
                                           session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                           conversation_async=Depends(ConversationAsync)):
    if not current_user.is_editor:
        raise Forbidden()
    conversation_id = str(conversation_id)
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    conversation = await _get_conversation_async(app_model, conversation_id, current_user, session)

    return await ConversationResp.to_conversation_details(conversation, conversation_async)


# @console_api.delete('/apps/{app_id}/chat-conversations/{conversation_id}',
#                     summary="删除 chat 类型的单个对话",
#                     description="根据 app_id 和 conversation_id 删除 chat 类型的对话。",
#                     tags=["conversation"])
async def chat_conversation_detail_api_delete(app_id: str, conversation_id: str,
                                              current_user: Account = Depends(login_user),
                                              session: AsyncSession = Depends(DbUtils.get_db_async_session)
                                              ):
    if not current_user.is_editor:
        raise Forbidden()
    conversation_id = str(conversation_id)
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    conversation = await session.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.app_id == app_model.id))
    conversation = conversation.scalar_one_or_none()
    if not conversation:
        raise NotFound("Conversation Not Exists.")

    conversation.is_deleted = True
    await session.commit()

    return {'result': 'success'}, 204


class ChatConversationDetailApi(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    @marshal_with(conversation_detail_fields)
    def get(self, app_model, conversation_id):
        if not current_user.is_editor:
            raise Forbidden()
        conversation_id = str(conversation_id)

        return _get_conversation(app_model, conversation_id)

    @setup_required
    @login_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    @account_initialization_required
    def delete(self, app_model, conversation_id):
        if not current_user.is_editor:
            raise Forbidden()
        conversation_id = str(conversation_id)

        conversation = db.session.query(Conversation) \
            .filter(Conversation.id == conversation_id, Conversation.app_id == app_model.id).first()

        if not conversation:
            raise NotFound("Conversation Not Exists.")

        conversation.is_deleted = True
        db.session.commit()

        return {'result': 'success'}, 204


api.add_resource(CompletionConversationApi, '/apps/<uuid:app_id>/completion-conversations')
api.add_resource(CompletionConversationDetailApi,
                 '/apps/<uuid:app_id>/completion-conversations/<uuid:conversation_id>')
api.add_resource(ChatConversationApi, '/apps/<uuid:app_id>/chat-conversations')
api.add_resource(ChatConversationDetailApi, '/apps/<uuid:app_id>/chat-conversations/<uuid:conversation_id>')


def _get_conversation(app_model, conversation_id):
    conversation = db.session.query(Conversation) \
        .filter(Conversation.id == conversation_id, Conversation.app_id == app_model.id).first()

    if not conversation:
        raise NotFound("Conversation Not Exists.")

    if not conversation.read_at:
        conversation.read_at = datetime.now().replace(tzinfo=None)
        conversation.read_account_id = current_user.id
        db.session.commit()

    return conversation


async def _get_conversation_async(app_model, conversation_id, current_user, session: AsyncSession):
    conversation = await session.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.app_id == app_model.id))

    conversation = conversation.scalar_one_or_none()

    if not conversation:
        raise NotFound("Conversation Not Exists.")

    if not conversation.read_at:
        conversation.read_at = datetime.now().replace(tzinfo=None)
        conversation.read_account_id = current_user.id
        await session.commit()

    return conversation
