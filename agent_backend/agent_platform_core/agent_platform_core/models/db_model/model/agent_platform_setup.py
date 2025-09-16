from agent_platform_basic.extensions.ext_database import db

"""
@Date    ：2024/7/15 9:33 
@Version: 1.0
@Description:

"""


class AgentPlatformSetup(db.Model):
    __tablename__ = 'agent_platform_setups'
    __table_args__ = (
        db.PrimaryKeyConstraint('version', name='agent_platform_setup_pkey'),
    )

    version = db.Column(db.String(255), nullable=False)
    setup_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
