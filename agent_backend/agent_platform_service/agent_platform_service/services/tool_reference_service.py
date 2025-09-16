from sqlalchemy import delete, insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.models.db_model.tool_reference import ToolReference


class ToolReferenceService:
    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    async def get_referenced_count(self, workflow_id: str) -> int:
        '''
        根据 workflow_id 查询此工具被哪些 workflow 引用
        '''
         # await self.session.execute(select(func.count()).where(ToolReference.reference_id == workflow_id))



    async def get_tool_reference(self, tool_reference_id: str):
        result = await self.session.execute(select(ToolReference).where(ToolReference.id == tool_reference_id))
        return result.scalars().first()

    async def get_tool_reference_by_reference_id(self, reference_id: str):
        result = await self.session.execute(select(ToolReference).where(ToolReference.reference_id == reference_id))
        return result.scalars().all()

    async def get_tool_reference_by_source_id(self, source_id: str):
        result = await self.session.execute(select(ToolReference).where(ToolReference.source_id == source_id))
        return result.scalars().all()

    async def create_tool_reference(self, source_id: str, reference_id: str):
        db_tool_reference = ToolReference(source_id=source_id, reference_id=reference_id)

        try:
            await self.session.execute(
                insert(ToolReference),
                {
                    "source_id": source_id,
                    "reference_id": reference_id,
                }
            )
        except IntegrityError as e:
            # 处理主键冲突等情况
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e.orig))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return db_tool_reference

    async def delete_tool_reference(self, reference_id: str, source_id: str):

        try:
            await self.session.execute(delete(ToolReference)
                                       .where(ToolReference.source_id == source_id)
                                       .where(ToolReference.reference_id == reference_id))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
