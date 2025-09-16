from sqlalchemy.orm import DeclarativeBase
from agent_platform_core.models.enum_model.engine import metadata
class Base(DeclarativeBase):
    metadata = metadata
