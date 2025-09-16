import json
from typing import Optional

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account
from agent_platform_core.models.enum_model.enums import CreatedByRole
from .workflow import Workflow

"""
@Date    ：2024/7/15 10:15 
@Version: 1.0
@Description:

"""


class WorkflowRun(db.Model):
    """
    Workflow Run

    Attributes:

    - id (uuid) Run ID
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - sequence_number (int) Auto-increment sequence number, incremented within the App, starting from 1
    - workflow_id (uuid) Workflow ID
    - type (string) Workflow type
    - triggered_from (string) Trigger source

        `debugging` for canvas debugging

        `app-run` for (published) app execution

    - version (string) Version
    - graph (text) Workflow canvas configuration (JSON)
    - inputs (text) Input parameters
    - status (string) Execution status, `running` / `succeeded` / `failed` / `stopped`
    - outputs (text) `optional` Output content
    - error (string) `optional` Error reason
    - elapsed_time (float) `optional` Time consumption (s)
    - total_tokens (int) `optional` Total tokens used
    - total_steps (int) Total steps (redundant), default 0
    - created_by_role (string) Creator role

        - `account` Console account

        - `end_user` End user

    - created_by (uuid) Runner ID
    - created_at (timestamp) Run time
    - finished_at (timestamp) End time
    """

    __tablename__ = 'workflow_runs'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='workflow_run_pkey'),
        db.Index('workflow_run_triggerd_from_idx', 'tenant_id', 'app_id', 'triggered_from'),
        db.Index('workflow_run_tenant_app_sequence_idx', 'tenant_id', 'app_id', 'sequence_number'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    app_id = db.Column(StringUUID, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    workflow_id = db.Column(StringUUID, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    triggered_from = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    graph = db.Column(db.Text)
    inputs = db.Column(db.Text)
    status = db.Column(db.String(255), nullable=False)
    outputs = db.Column(db.Text)
    error = db.Column(db.Text)
    elapsed_time = db.Column(db.Float, nullable=False, server_default=db.text('0'))
    total_tokens = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    total_steps = db.Column(db.Integer, server_default=db.text('0'))
    created_by_role = db.Column(db.String(255), nullable=False)
    created_by = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    finished_at = db.Column(db.DateTime)
    exceptions_count = db.Column(db.Integer, server_default=db.text("0"), nullable=True)


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

    @property
    def graph_dict(self):
        return json.loads(self.graph) if self.graph else None

    @property
    def inputs_dict(self):
        return json.loads(self.inputs) if self.inputs else None

    @property
    def outputs_dict(self):
        return json.loads(self.outputs) if self.outputs else None

    @property
    def message(self) -> Optional['Message']:
        from agent_platform_core.models.db_model.model import Message
        return db.session.query(Message).filter(
            Message.app_id == self.app_id,
            Message.workflow_run_id == self.id
        ).first()

    @property
    def workflow(self):
        return db.session.query(Workflow).filter(Workflow.id == self.workflow_id).first()

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'app_id': self.app_id,
            'sequence_number': self.sequence_number,
            'workflow_id': self.workflow_id,
            'type': self.type,
            'triggered_from': self.triggered_from,
            'version': self.version,
            'graph': self.graph_dict,
            'inputs': self.inputs_dict,
            'status': self.status,
            'outputs': self.outputs_dict,
            'error': self.error,
            'elapsed_time': self.elapsed_time,
            'total_tokens': self.total_tokens,
            'total_steps': self.total_steps,
            'created_by_role': self.created_by_role,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'finished_at': self.finished_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WorkflowRun':
        return cls(
            id=data.get('id'),
            tenant_id=data.get('tenant_id'),
            app_id=data.get('app_id'),
            sequence_number=data.get('sequence_number'),
            workflow_id=data.get('workflow_id'),
            type=data.get('type'),
            triggered_from=data.get('triggered_from'),
            version=data.get('version'),
            graph=json.dumps(data.get('graph')),
            inputs=json.dumps(data.get('inputs')),
            status=data.get('status'),
            outputs=json.dumps(data.get('outputs')),
            error=data.get('error'),
            elapsed_time=data.get('elapsed_time'),
            total_tokens=data.get('total_tokens'),
            total_steps=data.get('total_steps'),
            created_by_role=data.get('created_by_role'),
            created_by=data.get('created_by'),
            created_at=data.get('created_at'),
            finished_at=data.get('finished_at'),
        )
