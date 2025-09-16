from sqlalchemy import (
    Column,
    String,
    Text,
    TIMESTAMP,
    text, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ApplicationAudit(Base):
    __tablename__ = 'application_audit'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'))
    application_type = Column(String(100), nullable=False)
    applicant_id = Column(String(255), nullable=False)
    applicant = Column(String(255), nullable=False)
    reason = Column(Text)
    app_id = Column(String(255), nullable=False)
    app_type = Column(String(100), nullable=False)
    space_id = Column(String(255), nullable=False)
    space_name = Column(String(255))
    status = Column(String(100), nullable=False, server_default=text("'PENDING'::character varying"))
    denial_reason = Column(Text)
    reviewer_id = Column(String(255), nullable=False)
    reviewer = Column(String(255), nullable=False)
    application_time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    reviewed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    change_description = Column(Text)
    need_publish_tool = Column(Boolean, server_default=text('false'))
    tool_param = Column(Text)

    def as_dict(self):
        return {
            'id': str(self.id),
            'application_type': self.application_type,
            'applicant_id': self.applicant_id,
            'applicant': self.applicant,
            'reason': self.reason,
            'app_id': self.app_id,
            'space_id': self.space_id,
            'space_name': self.space_name,
            'status': self.status,
            'denial_reason': self.denial_reason,
            'reviewer_id': self.reviewer_id,
            'reviewer': self.reviewer,
            'application_time': self.application_time.isoformat() if self.application_time else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'change_description': self.change_description,
            'need_publish_tool': self.need_publish_tool,
        }
