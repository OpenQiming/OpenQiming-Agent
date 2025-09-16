import json

from sqlalchemy import ForeignKey

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
from agent_platform_core.models.db_model.model import App
from agent_platform_core.tools.entities.common_entities import I18nObject

"""
@Date    ：2024/7/15 8:53 
@Version: 1.0
@Description:

"""


class PublishedAppTool(db.Model):
    """
    The table stores the apps published as a tool for each person.
    """
    __tablename__ = 'tool_published_apps'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='published_app_tool_pkey'),
        db.UniqueConstraint('app_id', 'user_id', name='unique_published_app_tool')
    )

    # id of the tool provider
    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    # id of the app
    app_id = db.Column(StringUUID, ForeignKey('apps.id'), nullable=False)
    # who published this tool
    user_id = db.Column(StringUUID, nullable=False)
    # description of the tool, stored in i18n format, for human
    description = db.Column(db.Text, nullable=False)
    # llm_description of the tool, for LLM
    llm_description = db.Column(db.Text, nullable=False)
    # query description, query will be seem as a parameter of the tool, to describe this parameter to llm, we need this field
    query_description = db.Column(db.Text, nullable=False)
    # query name, the name of the query parameter
    query_name = db.Column(db.String(40), nullable=False)
    # name of the tool provider
    tool_name = db.Column(db.String(40), nullable=False)
    # author
    author = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def description_i18n(self) -> I18nObject:
        return I18nObject(**json.loads(self.description))

    @property
    def app(self) -> App:
        return db.session.query(App).filter(App.id == self.app_id).first()
