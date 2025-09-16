import logging
import traceback

from sqlalchemy import text

from agent_platform_basic.extensions.ext_database import async_db

from agent_platform_basic.models.db_model import Account

from agent_platform_service.controllers.console import console_api
from fastapi import Depends, HTTPException
from agent_platform_service.services.auth_service import login_user


@console_api.post("/subscribe")
async def insert_subscribe(request: dict, current_user: Account = Depends(login_user),):
    # plugin_id = request.get("plugin_id")
    plugin_name = request.get("plugin_name")
    author = request.get("author")

    plugin_id = f"{author}&&{plugin_name}"

    account_id = current_user.id
    tenant_id = request.get('tenant_id') or current_user.current_tenant_id


    try:
        async with async_db.AsyncSessionLocal() as session:
            # 检查是否已订阅
            check_sql = """
                SELECT EXISTS (
                    SELECT 1 FROM subscription 
                    WHERE account_id = :account_id AND plugin_id = :plugin_id
                )
            """
            result = await session.execute(
                text(check_sql),
                {"account_id": account_id, "plugin_id": plugin_id}
            )
            if result.scalar():
                raise HTTPException(400, detail="Already subscribed")

            # 插入新订阅
            insert_sql = """
                INSERT INTO subscription 
                (tenant_id, account_id, plugin_id, plugin_name)
                VALUES (:tenant_id, :account_id, :plugin_id, :plugin_name)
            """
            await session.execute(
                text(insert_sql),
                {
                    "tenant_id": tenant_id,
                    "account_id": account_id,
                    "plugin_id": plugin_id,
                    "plugin_name": plugin_name
                }
            )
            await session.commit()
        return {"code": 200, "msg": "success"}

    except KeyError:
        raise HTTPException(400, detail="Missing required fields")
    except Exception as e:
        logging.error(traceback.format_exc())
        await session.rollback()
        raise HTTPException(500, detail=str(e))


@console_api.delete("/subscribe")
async def delete_subscribe(request: dict, current_user: Account = Depends(login_user),):
    #plugin_id = request.get("plugin_id")
    plugin_name = request.get("plugin_name")
    author = request.get("author")

    plugin_id = f"{author}&&{plugin_name}"
    account_id = current_user.id
    tenant_id = request.get('tenant_id') or current_user.current_tenant_id
    try:
        async with async_db.AsyncSessionLocal() as session:
            check_sql = """
                SELECT EXISTS (
                    SELECT 1 FROM subscription 
                    WHERE account_id = :account_id AND plugin_id = :plugin_id
                )
            """
            result = await session.execute(
                text(check_sql),
                {"account_id": account_id, "plugin_id": plugin_id}
            )
            if not result.scalar():
                raise HTTPException(400, detail="没有可取消订阅")
            delete_sql = """
                delete from subscription
                WHERE account_id=:account_id and plugin_id=:plugin_id
            """
            await session.execute(
                text(delete_sql),
                {
                    "account_id": account_id,
                    "plugin_id": plugin_id,
                }
            )
            await session.commit()
        return {"code": 200, "msg": "success"}
    except KeyError:
        raise HTTPException(400, detail="Missing required fields")
    except Exception as e:
        logging.error(traceback.format_exc())
        await session.rollback()
        raise HTTPException(500, detail=str(e))


@console_api.post("/like")
async def insert_like(request: dict, current_user: Account = Depends(login_user),):
    # plugin_id = request.get("plugin_id")
    plugin_name = request.get("plugin_name")
    author = request.get("author")

    plugin_id = f"{author}&&{plugin_name}"

    account_id = current_user.id
    tenant_id = request.get('tenant_id') or current_user.current_tenant_id


    try:
        async with async_db.AsyncSessionLocal() as session:
            # 检查是否已订阅
            check_sql = """
                SELECT EXISTS (
                    SELECT 1 FROM plugin_like 
                    WHERE account_id = :account_id AND plugin_id = :plugin_id
                )
            """
            result = await session.execute(
                text(check_sql),
                {"account_id": account_id, "plugin_id": plugin_id}
            )
            if result.scalar():
                raise HTTPException(400, detail="Already subscribed")

            # 插入新订阅
            insert_sql = """
                INSERT INTO plugin_like 
                (tenant_id, account_id, plugin_id, plugin_name)
                VALUES (:tenant_id, :account_id, :plugin_id, :plugin_name)
            """
            await session.execute(
                text(insert_sql),
                {
                    "tenant_id": tenant_id,
                    "account_id": account_id,
                    "plugin_id": plugin_id,
                    "plugin_name": plugin_name
                }
            )
            await session.commit()
        return {"code": 200, "msg": "success"}

    except KeyError:
        raise HTTPException(400, detail="Missing required fields")
    except Exception as e:
        logging.error(traceback.format_exc())
        await session.rollback()
        raise HTTPException(500, detail=str(e))


@console_api.delete("/like")
async def delete_like(request: dict, current_user: Account = Depends(login_user),):
    #plugin_id = request.get("plugin_id")
    plugin_name = request.get("plugin_name")
    author = request.get("author")

    plugin_id = f"{author}&&{plugin_name}"
    account_id = current_user.id
    tenant_id = request.get('tenant_id') or current_user.current_tenant_id
    try:
        async with async_db.AsyncSessionLocal() as session:
            check_sql = """
                SELECT EXISTS (
                    SELECT 1 FROM plugin_like 
                    WHERE account_id = :account_id AND plugin_id = :plugin_id
                )
            """
            result = await session.execute(
                text(check_sql),
                {"account_id": account_id, "plugin_id": plugin_id}
            )
            if not result.scalar():
                raise HTTPException(400, detail="没有可取消点赞")
            delete_sql = """
                delete from plugin_like
                WHERE account_id=:account_id and plugin_id=:plugin_id
            """
            await session.execute(
                text(delete_sql),
                {
                    "account_id": account_id,
                    "plugin_id": plugin_id,
                }
            )
            await session.commit()
        return {"code": 200, "msg": "success"}
    except KeyError:
        raise HTTPException(400, detail="Missing required fields")
    except Exception as e:
        logging.error(traceback.format_exc())
        await session.rollback()
        raise HTTPException(500, detail=str(e))

@console_api.get("/subscribe/query_by_like")
async def like_subscribe(page: int = 1, page_size: int = 1000, current_user: Account = Depends(login_user),):
    offset = (page - 1) * page_size
    async with async_db.AsyncSessionLocal() as session:
        count_sql = text("""
            SELECT COUNT(DISTINCT plugin_id) 
            FROM subscription
        """)
        total = (await session.execute(count_sql)).scalar()

        data_sql = text("""
            SELECT 
                plugin_id, 
                plugin_name, 
                COUNT(*) as subscribe_count
            FROM subscription
            GROUP BY plugin_id, plugin_name
            ORDER BY subscribe_count DESC
            LIMIT :limit OFFSET :off
        """)
        result = await session.execute(data_sql, {
            "limit": page_size,
            "off": offset
        })
        rows = result.mappings().all()

    return {
        "data": rows,
        "total": total,
        "msg": "success"
    }