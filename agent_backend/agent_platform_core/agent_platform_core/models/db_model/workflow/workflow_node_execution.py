import json
from typing import Optional, Mapping, Any

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account
from agent_platform_core.models.enum_model.enums import CreatedByRole
from agent_platform_core.workflow.entities.workflow_node_execution import WorkflowNodeExecutionMetadataKey

"""
@Date    ：2024/7/15 10:19 
@Version: 1.0
@Description:

"""


class WorkflowNodeExecution(db.Model):
    """
    Workflow Node Execution

    - id (uuid) Execution ID
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - workflow_id (uuid) Workflow ID
    - triggered_from (string) Trigger source

        `single-step` for single-step debugging

        `workflow-run` for workflow execution (debugging / user execution)

    - workflow_run_id (uuid) `optional` Workflow run ID

        Null for single-step debugging.

    - index (int) Execution sequence number, used for displaying Tracing Node order
    - predecessor_node_id (string) `optional` Predecessor node ID, used for displaying execution path
    - node_id (string) Node ID
    - node_type (string) Node type, such as `start`
    - title (string) Node title
    - inputs (json) All predecessor node variable content used in the node
    - process_data (json) Node process data
    - outputs (json) `optional` Node output variables
    - status (string) Execution status, `running` / `succeeded` / `failed`
    - error (string) `optional` Error reason
    - elapsed_time (float) `optional` Time consumption (s)
    - execution_metadata (text) Metadata

        - total_tokens (int) `optional` Total tokens used

        - total_price (decimal) `optional` Total cost

        - currency (string) `optional` Currency, such as USD / RMB

    - created_at (timestamp) Run time
    - created_by_role (string) Creator role

        - `account` Console account

        - `end_user` End user

    - created_by (uuid) Runner ID
    - finished_at (timestamp) End time
    """

    __tablename__ = 'workflow_node_executions'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='workflow_node_execution_pkey'),
        db.Index('workflow_node_execution_workflow_run_idx', 'tenant_id', 'app_id', 'workflow_id',
                 'triggered_from', 'workflow_run_id'),
        db.Index('workflow_node_execution_node_run_idx', 'tenant_id', 'app_id', 'workflow_id',
                 'triggered_from', 'node_id'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    app_id = db.Column(StringUUID, nullable=False)
    workflow_id = db.Column(StringUUID, nullable=False)
    triggered_from = db.Column(db.String(255), nullable=False)
    workflow_run_id = db.Column(StringUUID)
    index = db.Column(db.Integer, nullable=False)
    predecessor_node_id = db.Column(db.String(255))
    node_id = db.Column(db.String(255), nullable=False)
    node_type = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    inputs = db.Column(db.Text)
    process_data = db.Column(db.Text)
    outputs = db.Column(db.Text)
    status = db.Column(db.String(255), nullable=False)
    error = db.Column(db.Text)
    elapsed_time = db.Column(db.Float, nullable=False, server_default=db.text('0'))
    execution_metadata = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    created_by_role = db.Column(db.String(255), nullable=False)
    created_by = db.Column(StringUUID, nullable=False)
    finished_at = db.Column(db.DateTime)

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
    def inputs_dict(self):
        return json.loads(self.inputs) if self.inputs else None

    @property
    def outputs_dict(self):
        return json.loads(self.outputs) if self.outputs else None

    @property
    def process_data_dict(self):
        return json.loads(self.process_data) if self.process_data else None

    @property
    def execution_metadata_dict(self):
        return json.loads(self.execution_metadata) if self.execution_metadata else None

    @property
    def extras(self):
        from agent_platform_core.tools.tool_manager import ToolManager
        extras = {}
        if self.execution_metadata_dict:
            from agent_platform_core.workflow.nodes import NodeType
            if self.node_type == NodeType.TOOL.value and 'tool_info' in self.execution_metadata_dict:
                tool_info = self.execution_metadata_dict['tool_info']
                extras['icon'] = ToolManager.get_tool_icon(
                    tenant_id=self.tenant_id,
                    provider_type=tool_info['provider_type'],
                    provider_id=tool_info['provider_id']
                )

        return extras

    def update_from_mapping(
            self,
            inputs: Optional[Mapping[str, Any]] = None,
            process_data: Optional[Mapping[str, Any]] = None,
            outputs: Optional[Mapping[str, Any]] = None,
            metadata: Optional[Mapping[WorkflowNodeExecutionMetadataKey, Any]] = None,
    ) -> None:
        """
        Update the model from mappings.

        Args:
            inputs: The inputs to update
            process_data: The process data to update
            outputs: The outputs to update
            metadata: The metadata to update
        """
        if inputs is not None:
            self.inputs = json.dumps(inputs, ensure_ascii=False)
        if process_data is not None:
            self.process_data = json.dumps(process_data, ensure_ascii=False)
        if outputs is not None:
            self.outputs = json.dumps(outputs, ensure_ascii=False)
        if metadata is not None:
            self.execution_metadata = json.dumps(metadata, ensure_ascii=False)

    def to_dict(self):
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "app_id": str(self.app_id),
            "workflow_id": str(self.workflow_id),
            "triggered_from": self.triggered_from,
            "workflow_run_id": str(self.workflow_run_id) if self.workflow_run_id else None,
            "index": self.index,
            "predecessor_node_id": self.predecessor_node_id,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "title": self.title,
            "inputs": self.inputs_dict,
            "process_data": self.process_data_dict,
            "outputs": self.outputs_dict,
            "status": self.status,
            "error": self.error,
            "elapsed_time": self.elapsed_time,
            "execution_metadata": self.execution_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by_role": self.created_by_role,
            "created_by": str(self.created_by),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }