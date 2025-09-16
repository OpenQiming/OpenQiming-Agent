from sqlalchemy import Column, String, Boolean, DateTime, text, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GlobalUserPermissions(Base):
    __tablename__ = 'global_user_permissions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='global_user_permission_pkey'),
        UniqueConstraint('user_id', name='unique_user_id')
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=text('uuid_generate_v4()'))
    user_id = Column(String(255), nullable=False)
    can_view_all = Column(Boolean, default=False, server_default=text('FALSE'))
    can_edit_all = Column(Boolean, default=False, server_default=text('FALSE'))
    operator = Column(String(255))
    created_at = Column(DateTime, default=text('CURRENT_TIMESTAMP'))

    def as_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'can_view_all': self.can_view_all,
            'can_edit_all': self.can_edit_all,
            'operator': self.operator,
            'created_at': self.created_at.isoformat()
        }
