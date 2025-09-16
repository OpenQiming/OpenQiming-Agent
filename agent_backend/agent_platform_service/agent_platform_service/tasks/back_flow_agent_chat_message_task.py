import logging

from celery import shared_task
from agent_platform_core.models.db_model.model import App
from agent_platform_basic.models.db_model.tenant import Tenant
from agent_platform_basic.extensions.ext_database import async_db
from sqlalchemy import select, func
from agent_platform_basic.models.enum_model.application_audit import ApplicationType
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_core.models.db_model.model import Conversation
from aiokafka import AIOKafkaProducer
from agent_platform_common.configs import agent_platform_config
import traceback
import json

kafka_ip = agent_platform_config.KAFKA_IP
kafka_topic = agent_platform_config.KAFKA_TOPIC
host_ip = agent_platform_config.HOST_IP
kafka_user = agent_platform_config.KAFKA_USER
kafka_password = agent_platform_config.KAFKA_PASSWORD

async def send_kafka_message(topic: str, message: dict):
    print(kafka_ip, kafka_topic, message)
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_ip,
        acks="all",
        linger_ms=5,
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        # SASL
        security_protocol="SASL_PLAINTEXT",
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=kafka_user,
        sasl_plain_password=kafka_password,
    )
    try:
        await producer.start()
        await producer.send_and_wait(topic, message)
    finally:
        await producer.stop()

# @shared_task(queue='backflow')
async def back_flow_agent_chat_message_task(kafka_msg):
    try:
        async with async_db.AsyncSessionLocal() as session:
            agentID = kafka_msg["svcName"]
            stmt = select(App).where(App.id == agentID)
            result = await session.execute(stmt)
            app = result.scalars().first()

            if not app:
                raise ValueError(f"应用不存在: {agentID}")
            # kafka_msg["agentName"] = app.name
            kafka_msg["svcName"] = app.name

            stmt = select(Tenant).where(Tenant.id == app.tenant_id)
            result = await session.execute(stmt)
            tenant = result.scalars().first()

            status_map = {
                ApplicationType.NORMAL.value: "个人空间",
                ApplicationType.PROJECT.value: "项目空间",
            }

            status = status_map.get(tenant.status, "")
            # kafka_msg["workspaceId"] = f"{status}-{tenant.name}"
            kafka_msg["ip"] = host_ip

            stmt = select(func.count()).where(
                Conversation.app_id == agentID,
                Conversation.mode == AppMode.AGENT_CHAT.value
            )
            result = await session.execute(stmt)
            count = result.scalar()
            # kafka_msg["callCount"] = count


        print("kafka_msg::::::", kafka_msg)

        topic = kafka_topic
        if kafka_ip:
            await send_kafka_message(topic, kafka_msg)
    except:
        logging.info(f"数据回流报错 {traceback.format_exc()}")
        pass