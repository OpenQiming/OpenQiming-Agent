from datetime import datetime
from decimal import Decimal

import pytz
from flask import jsonify
from flask_login import current_user
from flask_restful import Resource, reqparse

from agent_platform_basic.extensions.ext_database import async_db
from sqlalchemy import text
from agent_platform_basic.libs.helper import datetime_string
from agent_platform_basic.libs.login import login_required
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.app.wraps import get_app_model
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from collections import defaultdict
import httpx
from fastapi import Depends, Form
import json

from agent_platform_service.services.auth_service import login_user
from agent_platform_basic.models.db_model import AccountIntegrate, InvitationCode, Account
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.helper import async_ssrf_proxy
from agent_platform_service.controllers.console import console_api
from fastapi import FastAPI, File, UploadFile, HTTPException
import logging

# 1.智能体日志接口
# @setup_required
# @login_required
# @account_initialization_required
# @get_app_model
@console_api.post("/agent_log")
async def get_agent_log(request: dict):
    try:
        app_id = request.get("app_id","")
        logging.info(f"接收到app_id: {app_id}")

        query = """
        SELECT 
            c.id,
            c.created_at,
            c.updated_at,
            COUNT(m.id) AS message_count,
            a.username
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        JOIN accounts a ON c.from_account_id = a.id
        WHERE c.app_id = :app_id
        GROUP BY c.id, a.username;
        """
        arg_dict = {"app_id": app_id}

        async with async_db.AsyncSessionLocal() as session:  #
            rs = await session.execute(text(query), arg_dict)
            formatted_results=[]
            for row in rs:
                print("row: ", row)
                created_at_time = row[1]
                updated_at_time = row[2]
                num_message = row[3]
                username = row[4]
                print("created_at_time: ", created_at_time)
                print("updated_at_time: ", updated_at_time)
                print("num_message: ", num_message)
                print("username: ", username)
                formatted_results.append({
                    "create_time": created_at_time,
                    "update_time": updated_at_time,
                    "num_message": str(num_message),
                    "user": username
                })


            # formatted_results = [
            #     {
            #         "num_message": str(row[3]),
            #         "user": row[4]
            #
            #     }
            #     for row in rs
            # ]
        
        return {"conversation_list": formatted_results, "status": "successful"}
    except Exception as e:
        logging.error(f"查询智能体日志发生错误: {e}")
        raise HTTPException(status_code=500, detail="智能体日志查询失败")


@console_api.post("/agent_monitor")
async def get_statistics(request: dict) -> dict:
    """智能体监控接口，统计应用的对话数据"""
    app_id = request.get("app_id")
    days = request.get("days", 7)  # Default to 7 days if 'days' is not provided
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)

    logging.debug(f"Start Date: {start_date}, App ID: {app_id}, Days: {days}")
    
    # Generate date list for the past 'days' days
    date_list = [(start_date + datetime.timedelta(days=i)).isoformat() for i in range(days)]

    # Initialize data dictionaries for daily statistics
    daily_active_users_dict = defaultdict(int)
    daily_conversations_dict = defaultdict(int)

    async with AsyncSessionLocal() as session:
        try:
            # SQLAlchemy query using `select` for async queries
            query = """
            WITH daily_data AS (
                SELECT 
                    DATE(created_at) AS date, 
                    COUNT(DISTINCT from_account_id) AS active_users, 
                    COUNT(id) AS conversations
                FROM conversations
                WHERE app_id = :app_id AND created_at >= :start_date AND is_deleted = FALSE
                GROUP BY DATE(created_at)
            ),
            total_conversations AS (
                SELECT COUNT(id) AS total_count
                FROM conversations
                WHERE app_id = :app_id AND created_at >= :start_date AND is_deleted = FALSE
            ),
            total_users AS (
                SELECT COUNT(DISTINCT from_account_id) AS total_count
                FROM conversations
                WHERE app_id = :app_id AND is_deleted = FALSE
            )
            SELECT 
                COALESCE(dd.date, :today::date) AS date,
                COALESCE(dd.active_users, 0) AS active_users,
                COALESCE(dd.conversations, 0) AS conversations,
                tc.total_count AS total_conversations,
                tu.total_count AS total_users
            FROM daily_data dd
            RIGHT JOIN generate_series(:start_date::date, :today::date, '1 day'::interval) gs(date) ON dd.date = gs.date::date
            CROSS JOIN total_conversations tc
            CROSS JOIN total_users tu
            ORDER BY date;
            """
            
            result = await session.execute(
                text(query),
                {
                    "app_id": app_id,
                    "start_date": start_date,
                    "today": today
                }
            )

            results = result.fetchall()

            # Variables to store final statistics
            total_conversations = 0
            total_users = 0
            daily_active_users = []
            daily_conversations = []

            # Fill data dictionaries with query results
            for record in results:
                date = record['date'].isoformat()
                daily_active_users_dict[date] = record['active_users']
                daily_conversations_dict[date] = record['conversations']
                total_conversations = record['total_conversations']
                total_users = record['total_users']

            # Fill daily active users and daily conversations lists
            daily_active_users = [daily_active_users_dict[date] for date in date_list]
            daily_conversations = [daily_conversations_dict[date] for date in date_list]

            # Calculate average conversations per day
            average_conversations = total_conversations / days if days > 0 else 0
            logging.debug(f"Total Users: {total_users}")
            logging.debug(f"Average Conversations: {average_conversations}")

            # Assuming constant token output speed
            token_output_speed = 15

            return {
                "total_conversations": total_conversations,
                "average_conversations": average_conversations,
                "total_users": total_users,
                "daily_active_users": daily_active_users,
                "daily_conversations": daily_conversations,
                "token_output_speed": token_output_speed,
                "status": "successful"
            }

        except Exception as e:
            logging.error(f"Error fetching statistics: {e}")
            return {
                "total_conversations": 0,
                "average_conversations": 0,
                "total_users": 0,
                "daily_active_users": [0] * days,  # Fill 0 for all days
                "daily_conversations": [0] * days,
                "token_output_speed": 0,
                "status": "failure"
            }
