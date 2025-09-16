from agent_platform_basic.extensions.ext_database import Base
class ToolReference(Base):
    __tablename__ = 'tool_reference'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tool_reference_primary_key'),
        UniqueConstraint('source_id', 'reference_id', name='unique_reference')
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(255), nullable=False)
    reference_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    def as_dict(self):
        return {
            'id': str(self.id),
            'source_id': self.source_id,
            'reference_id': self.reference_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

