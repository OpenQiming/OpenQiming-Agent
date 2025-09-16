import asyncio
from datetime import datetime

from sqlalchemy import func, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from agent_platform_core import contexts
from agent_platform_core.variables import (
    SecretVariable,
    Variable,
)
from agent_platform_core.factories import variable_factory
from agent_platform_core.helper import encrypter
import json
from collections.abc import Sequence
from enum import Enum
from typing import Any, Optional, Mapping

from pydantic import BaseModel

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs import helper
from agent_platform_basic.models.db_model import StringUUID, Account


class EnvironmentType(str, Enum):
    STRING = 'string'
    NUMBER = 'number'
    SECRET = 'secret'


class EnvironmentVariable(BaseModel):
    name: str
    value: Any
    value_type: EnvironmentType
    exportable: bool

    def export(self):
        if not self.exportable:
            raise ValueError(f'environment variable {self.name} is not exportable')
        if self.value_type == EnvironmentType.SECRET:
            cp = self.model_copy()
            cp.value = None
            return cp.model_dump(mode='json')
        return self.model_dump(mode='json')


class DBEnvironmentVariable(BaseModel):
    data: Sequence[EnvironmentVariable]


class Workflow(db.Model):
    """
    Workflow, for `Workflow App` and `Chat App workflow mode`.

    Attributes:

    - id (uuid) Workflow ID, pk
    - tenant_id (uuid) Workspace ID
    - app_id (uuid) App ID
    - type (string) Workflow type

        `workflow` for `Workflow App`

        `chat` for `Chat App workflow mode`

    - version (string) Version

        `draft` for draft version (only one for each app), other for version number (redundant)

    - graph (text) Workflow canvas configuration (JSON)

        The entire canvas configuration JSON, including Node, Edge, and other configurations

        - nodes (array[object]) Node list, see Node Schema

        - edges (array[object]) Edge list, see Edge Schema

    - created_by (uuid) Creator ID
    - created_at (timestamp) Creation time
    - updated_by (uuid) `optional` Last updater ID
    - updated_at (timestamp) `optional` Last update time
    """

    __tablename__ = "workflows"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="workflow_pkey"),
        db.Index("workflow_version_idx", "tenant_id", "app_id", "version"),
    )

    id: Mapped[str] = mapped_column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    tenant_id: Mapped[str] = mapped_column(StringUUID, nullable=False)
    app_id: Mapped[str] = mapped_column(StringUUID, nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(255), nullable=False)
    graph: Mapped[str] = mapped_column(Text)
    _features: Mapped[str] = mapped_column("features", Text)
    created_by: Mapped[str] = mapped_column(StringUUID, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)")
    )
    updated_by: Mapped[Optional[str]] = mapped_column(StringUUID)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(), server_onupdate=func.current_timestamp()
    )
    _environment_variables: Mapped[str] = mapped_column(
        "environment_variables", Text, nullable=False, server_default="{}"
    )
    _conversation_variables: Mapped[str] = mapped_column(
        "conversation_variables", Text, nullable=False, server_default="{}"
    )
    example = db.Column(db.Text, nullable=True)
    is_enable = db.Column(db.Boolean)
    version_app_name = db.Column(db.Text)

    @property
    def created_by_account(self):
        return db.session.get(Account, self.created_by)

    @property
    def updated_by_account(self):
        return db.session.get(Account, self.updated_by) if self.updated_by else None

    @property
    def graph_dict(self) -> Mapping[str, Any]:
        return json.loads(self.graph) if self.graph else {}

    @property
    def features(self) -> str:
        """
        Convert old features structure to new features structure.
        """
        if not self._features:
            return self._features
        # 兼容前端旧代码，暂不启用
        # features = json.loads(self._features)
        # if features.get("file_upload", {}).get("image", {}).get("enabled", False):
        #     image_enabled = True
        #     image_number_limits = int(features["file_upload"]["image"].get("number_limits", 1))
        #     image_transfer_methods = features["file_upload"]["image"].get(
        #         "transfer_methods", ["remote_url", "local_file"]
        #     )
        #     features["file_upload"]["enabled"] = image_enabled
        #     features["file_upload"]["number_limits"] = image_number_limits
        #     features["file_upload"]["allowed_file_upload_methods"] = image_transfer_methods
        #     features["file_upload"]["allowed_file_types"] = ["image"]
        #     features["file_upload"]["allowed_file_extensions"] = []
        #     del features["file_upload"]["image"]
        #     self._features = json.dumps(features)
        return self._features

    @features.setter
    def features(self, value: str) -> None:
        self._features = value

    @property
    def features_dict(self) -> Mapping[str, Any]:
        return json.loads(self.features) if self.features else {}

    def user_input_form(self, to_old_structure: bool = False) -> list:
        # get start node from graph
        if not self.graph:
            return []

        graph_dict = self.graph_dict
        if "nodes" not in graph_dict:
            return []

        start_node = next((node for node in graph_dict["nodes"] if node["data"]["type"] == "start"), None)
        if not start_node:
            return []

        # get user_input_form from start node
        variables = start_node.get("data", {}).get("variables", [])

        if to_old_structure:
            old_structure_variables = []
            for variable in variables:
                old_structure_variables.append({variable["type"]: variable})

            return old_structure_variables

        return variables

    @property
    def unique_hash(self) -> str:
        """
        Get hash of workflow.

        :return: hash
        """
        entity = {"graph": self.graph_dict, "features": self.features_dict}

        return helper.generate_text_hash(json.dumps(entity, sort_keys=True))

    @property
    def tool_published(self) -> bool:
        from ..tools import WorkflowToolProvider

        return (
            db.session.query(WorkflowToolProvider).filter(WorkflowToolProvider.app_id == self.app_id).first()
            is not None
        )

    @property
    def environment_variables(self) -> Sequence[Variable]:
        # TODO: find some way to init `self._environment_variables` when instance created.
        if self._environment_variables is None:
            self._environment_variables = '{}'
        try:
            tenant_id = contexts.tenant_id.get()
        except:
            tenant_id = self.tenant_id  # TODO fix contexts.tenant_id.get() for all others API-requests

        environment_variables_dict: dict[str, Any] = json.loads(self._environment_variables)
        results = [variable_factory.build_environment_variable_from_mapping(v) for v in environment_variables_dict.values()]

        # decrypt secret variables value
        decrypt_func = (
            lambda var: var.model_copy(
                update={'value': encrypter.decrypt_token(tenant_id=tenant_id, token=var.value)}
            )
            if isinstance(var, SecretVariable)
            else var
        )
        results = list(map(decrypt_func, results))
        return results

    async def async_environment_variables(self) -> Sequence[Variable]:
        # TODO: find some way to init `self._environment_variables` when instance created.
        if self._environment_variables is None:
            self._environment_variables = '{}'
        try:
            tenant_id = contexts.tenant_id.get()
        except:
            tenant_id = self.tenant_id  # TODO fix contexts.tenant_id.get() for all others API-requests

        environment_variables_dict: dict[str, Any] = json.loads(self._environment_variables)
        results = [variable_factory.build_environment_variable_from_mapping(v) for v in environment_variables_dict.values()]

        # decrypt secret variables value
        async def decrypt_func(var):
            if isinstance(var, SecretVariable):
                return var.model_copy(
                    update={'value': await encrypter.async_decrypt_token(tenant_id=tenant_id, token=var.value)})
            else:
                return var

        results = await asyncio.gather(*[decrypt_func(result) for result in results])
        return results

    @environment_variables.setter
    def environment_variables(self, encrypted_vars):
        environment_variables_json = json.dumps(
            {var.name: var.model_dump() for var in encrypted_vars},
            ensure_ascii=False,
        )
        self._environment_variables = environment_variables_json
    #TODO should output secret values

    def to_dict(self, *, include_secret: bool = False) -> Mapping[str, Any]:
        environment_variables = list(self.environment_variables)
        environment_variables = [
            v if not isinstance(v, SecretVariable) or include_secret else v.model_copy(update={"value": ""})
            for v in environment_variables
        ]

        result = {
            "graph": self.graph_dict,
            "features": self.features_dict,
            "environment_variables": [var.model_dump(mode="json") for var in environment_variables],
            "conversation_variables": [var.model_dump(mode="json") for var in self.conversation_variables],
        }
        return result

    @property
    def conversation_variables(self) -> Sequence[Variable]:
        # TODO: find some way to init `self._conversation_variables` when instance created.
        if self._conversation_variables is None:
            self._conversation_variables = "{}"

        variables_dict: dict[str, Any] = json.loads(self._conversation_variables)
        results = [variable_factory.build_conversation_variable_from_mapping(v) for v in variables_dict.values()]
        return results

    @conversation_variables.setter
    def conversation_variables(self, value: Sequence[Variable]) -> None:
        self._conversation_variables = json.dumps(
            {var.name: var.model_dump() for var in value},
            ensure_ascii=False,
        )
