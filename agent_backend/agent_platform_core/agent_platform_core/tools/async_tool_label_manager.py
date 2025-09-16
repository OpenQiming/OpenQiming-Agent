from sqlalchemy import delete, select

from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_core.models.db_model.tools import ToolLabelBinding

from agent_platform_core.tools.entities.values import default_tool_label_name_list
from agent_platform_core.tools.provider.api_tool_provider import ApiToolProviderController
from agent_platform_core.tools.provider.builtin_tool_provider import BuiltinToolProviderController
from agent_platform_core.tools.provider.tool_provider import ToolProviderController
from agent_platform_core.tools.provider.workflow_tool_provider import WorkflowToolProviderController


class AsyncToolLabelManager:
    @classmethod
    def filter_tool_labels(cls, tool_labels: list[str]) -> list[str]:
        """
        Filter tool labels
        """
        tool_labels = [label for label in tool_labels if label in default_tool_label_name_list]
        return list(set(tool_labels))

    @classmethod
    async def update_tool_labels(cls, controller: ToolProviderController, labels: list[str]):
        """
        Update tool labels
        """
        labels = cls.filter_tool_labels(labels)

        if isinstance(controller, ApiToolProviderController | WorkflowToolProviderController):
            provider_id = controller.provider_id
        else:
            raise ValueError('Unsupported tool type')

        async with async_db.AsyncSessionLocal() as session:

            await session.execute(delete(ToolLabelBinding).filter(ToolLabelBinding.tool_id == provider_id))
            # insert new labels
            for label in labels:
                session.add(ToolLabelBinding(
                    tool_id=provider_id,
                    tool_type=controller.provider_type.value,
                    label_name=label,
                ))

    @classmethod
    async def get_tool_labels(cls, controller: ToolProviderController) -> list[str]:
        """
        Get tool labels
        """
        if isinstance(controller, ApiToolProviderController | WorkflowToolProviderController):
            provider_id = controller.provider_id
        elif isinstance(controller, BuiltinToolProviderController):
            return controller.tool_labels
        else:
            raise ValueError('Unsupported tool type')

        async with async_db.AsyncSessionLocal() as session:
            query = await session.execute(select(ToolLabelBinding.label_name).filter(ToolLabelBinding.tool_id == provider_id,
                                                                       ToolLabelBinding.tool_type == controller.provider_type.value))
            labels: list[ToolLabelBinding] = query.scalars().all()

        return [label.label_name for label in labels]

    @classmethod
    async def get_tools_labels(cls, tool_providers: list[ToolProviderController]) -> dict[str, list[str]]:
        """
        Get tools labels

        :param tool_providers: list of tool providers

        :return: dict of tool labels
            :key: tool id
            :value: list of tool labels
        """
        if not tool_providers:
            return {}

        for controller in tool_providers:
            if not isinstance(controller, ApiToolProviderController | WorkflowToolProviderController):
                raise ValueError('Unsupported tool type')

        provider_ids = [controller.provider_id for controller in tool_providers]

        async with async_db.AsyncSessionLocal() as session:
            rs = await session.execute(select(ToolLabelBinding).filter(
            ToolLabelBinding.tool_id.in_(provider_ids)))
            labels: list[ToolLabelBinding] = rs.scalars().all()

        tool_labels = {
            label.tool_id: [] for label in labels
        }

        for label in labels:
            tool_labels[label.tool_id].append(label.label_name)

        return tool_labels
