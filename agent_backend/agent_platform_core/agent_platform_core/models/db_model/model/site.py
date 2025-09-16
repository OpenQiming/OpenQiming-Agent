from flask import current_app, request
from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, Text, Boolean

from agent_platform_basic.extensions.ext_database import db, Base
from agent_platform_basic.libs.helper import generate_string
from agent_platform_basic.models.db_model import StringUUID

""" 
@Date    ：2024/7/14 23:49 
@Version: 1.0
@Description:

"""


class Site(Base):
    __tablename__ = 'sites'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='site_pkey'),
        Index('site_app_id_idx', 'app_id'),
        Index('site_code_idx', 'code', 'status')
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    app_id = Column(StringUUID, nullable=False)
    title = Column(String(255), nullable=False)
    icon = Column(String(255))
    icon_background = Column(String(255))
    description = Column(Text)
    default_language = Column(String(255), nullable=False, server_default=text("'zh-Hans'"))
    chat_color_theme = Column(String(255))
    chat_color_theme_inverted = Column(Boolean, nullable=False, server_default=text('false'))
    copyright = Column(String(255))
    privacy_policy = Column(String(255))
    show_workflow_steps = Column(Boolean, nullable=False, server_default=text('true'))
    custom_disclaimer = Column(String(255), nullable=True)
    customize_domain = Column(String(255))
    customize_token_strategy = Column(String(255), nullable=False)
    prompt_public = Column(Boolean, nullable=False, server_default=text('false'))
    status = Column(String(255), nullable=False, server_default=text("'normal'::character varying"))
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    code = Column(String(255))

    @staticmethod
    def generate_code(n):
        while True:
            result = generate_string(n)
            while db.session.query(Site).filter(Site.code == result).count() > 0:
                result = generate_string(n)

            return result

    @property
    def app_base_url(self):
        return (
            current_app.config['APP_WEB_URL'] if current_app.config['APP_WEB_URL'] else request.host_url.rstrip('/'))
