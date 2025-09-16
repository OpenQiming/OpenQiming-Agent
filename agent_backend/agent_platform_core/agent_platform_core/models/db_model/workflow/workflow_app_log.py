from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account
from agent_platform_core.models.enum_model.enums import CreatedByRole
from .workflow_run import WorkflowRun

"""

@Date    ：2024/7/15 10:26 
@Version: 1.0
@Description:

"""


class WorkflowAppLog(db.Model):
    """
    Workflow App execution log, excluding workflow debugging records.

    Attributes:

    - id (uuid) run ID
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - workflow_id (uuid) Associated Workflow ID
    - workflow_run_id (uuid) Associated Workflow Run ID
    - created_from (string) Creation source

        `service-api` App Execution OpenAPI

        `web-app` WebApp

        `installed-app` Installed App

    - created_by_role (string) Creator role

        - `account` Console account

        - `end_user` End user

    - created_by (uuid) Creator ID, depends on the user table according to created_by_role
    - created_at (timestamp) Creation time
    """

    __tablename__ = 'workflow_app_logs'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='workflow_app_log_pkey'),
        db.Index('workflow_app_log_app_idx', 'tenant_id', 'app_id'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    app_id = db.Column(StringUUID, nullable=False)
    workflow_id = db.Column(StringUUID, nullable=False)
    workflow_run_id = db.Column(StringUUID, nullable=False)
    created_from = db.Column(db.String(255), nullable=False)
    created_by_role = db.Column(db.String(255), nullable=False)
    created_by = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def workflow_run(self):
        return WorkflowRun.query.get(self.workflow_run_id)

    @property
    def created_by_account(self):
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return db.session.query(Account).get(self.created_by) \
            if created_by_role == CreatedByRole.ACCOUNT else None

    @property
    def created_by_end_user(self):
        from agent_platform_core.models.db_model.model import EndUser
        created_by_role = CreatedByRole.value_of(self.created_by_role)
        return EndUser.query.get(self.created_by) \
            if created_by_role == CreatedByRole.END_USER else None
