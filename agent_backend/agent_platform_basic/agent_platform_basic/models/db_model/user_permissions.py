from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, text, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class UserPermissions(Base):
    __tablename__ = 'user_permissions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_permission_pkey'),
        UniqueConstraint('user_id', 'app_id', name='unique_user_app')
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    app_id = Column(String(255), nullable=False)
    can_view = Column(Boolean, default=False, server_default=text('FALSE'))
    can_edit = Column(Boolean, default=False, server_default=text('FALSE'))
    operator = Column(String(255))
    created_at = Column(DateTime, default=text('CURRENT_TIMESTAMP'))

    def as_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'app_id': self.app_id,
            'can_view': self.can_view,
            'can_edit': self.can_edit,
            'operator': self.operator,
            'created_at': self.created_at.isoformat()
        }
