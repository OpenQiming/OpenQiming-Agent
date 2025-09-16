from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.tools import ToolLabelBinding

from agent_platform_core.tools.entities.values import default_tool_label_name_list
from agent_platform_core.tools.plugin_tool.provider import PluginToolProviderController
from agent_platform_core.tools.provider.api_tool_provider import ApiToolProviderController
from agent_platform_core.tools.provider.builtin_tool_provider import BuiltinToolProviderController
from agent_platform_core.tools.provider.tool_provider import ToolProviderController
from agent_platform_core.tools.provider.workflow_tool_provider import WorkflowToolProviderController


class ToolLabelManager:
    @classmethod
    def filter_tool_labels(cls, tool_labels: list[str]) -> list[str]:
        """
        Filter tool labels
        """
        tool_labels = [label for label in tool_labels if label in default_tool_label_name_list]
        return list(set(tool_labels))

    @classmethod
    def update_tool_labels(cls, controller: ToolProviderController, labels: list[str]):
        """
        Update tool labels
        """
        labels = cls.filter_tool_labels(labels)

        if isinstance(controller, ApiToolProviderController | WorkflowToolProviderController):
            provider_id = controller.provider_id
        else:
            raise ValueError('Unsupported tool type')

        # delete old labels
        db.session.query(ToolLabelBinding).filter(
            ToolLabelBinding.tool_id == provider_id
        ).delete()

        # insert new labels
        for label in labels:
            db.session.add(ToolLabelBinding(
                tool_id=provider_id,
                tool_type=controller.provider_type.value,
                label_name=label,
            ))

        db.session.commit()

    @classmethod
    def get_tool_labels(cls, controller: ToolProviderController) -> list[str]:
        """
        Get tool labels
        """
        if isinstance(controller, ApiToolProviderController | WorkflowToolProviderController):
            provider_id = controller.provider_id
        elif isinstance(controller, BuiltinToolProviderController | PluginToolProviderController):
            return controller.tool_labels
        else:
            raise ValueError('Unsupported tool type')

        labels: list[ToolLabelBinding] = db.session.query(ToolLabelBinding.label_name).filter(
            ToolLabelBinding.tool_id == provider_id,
            ToolLabelBinding.tool_type == controller.provider_type.value,
        ).all()

        return [label.label_name for label in labels]

    @classmethod
    def get_tool_labels_new(cls, name):
        name_label_mapping = {
            "simple_code": "代码执行",
            "eval_expression": "代码执行",
            "json_replace": "代码执行",
            "json_delete": "代码执行",
            "parse": "代码执行",
            "json_insert": "代码执行",
            "line_chart": "多模态",
            "bar_chart": "多模态",
            "pie_chart": "多模态",
            "weekday": "通用",
            "current_time": "通用",
            "sql_query": "通用",
            "mcp_sse_list_tools": "通用",
            "mcp_sse_call_tool": "通用",
            "sql_execute": "通用",
            "text2sql": "通用",
            "table_schema": "通用",
            "csv_query": "通用",
            "regex_extract": "通用",
            "mcp_list_tools": "通用",
            "mcp_call_tool": "通用"
        }

        return [name_label_mapping.get(name, "通用")]

    @classmethod
    def get_tool_create_time(cls, name):
        name_time_mapping = {
            "simple_code": "2024-04-04 10:53:00",
            "eval_expression": "2024-07-04 13:51:00",
            "json_replace": "2024-08-03 13:45:01",
            "json_delete": "2024-05-04 13:33:02",
            "parse": "2024-07-04 14:51:04",
            "json_insert": "2024-05-05 17:51:14",
            "line_chart": "2024-01-09 09:51:06",
            "bar_chart": "2025-05-04 13:51:00",
            "pie_chart": "2025-06-04 13:51:00",
            "weekday": "2024-06-09 13:51:00",
            "current_time": "2024-12-04 13:51:00",
            "sql_query": "2024-10-04 13:51:54",
            "mcp_sse_list_tools": "2024-01-09 13:51:00",
            "mcp_sse_call_tool": "2024-05-26 13:51:00",
            "sql_execute": "2025-05-04 13:51:41",
            "text2sql": "2024-05-04 13:51:00",
            "table_schema": "2024-05-04 13:51:00",
            "csv_query": "2024-05-04 13:51:31",
            "regex_extract": "2024-05-04 18:51:44",
            "mcp_list_tools": "2024-02-04 20:11:40",
            "mcp_call_tool": "2024-08-04 15:11:30"
        }

        return name_time_mapping.get(name, "2024-05-04 13:51:00")

    @classmethod
    def get_tools_labels(cls, tool_providers: list[ToolProviderController]) -> dict[str, list[str]]:
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

        labels: list[ToolLabelBinding] = db.session.query(ToolLabelBinding).filter(
            ToolLabelBinding.tool_id.in_(provider_ids)
        ).all()

        tool_labels = {
            label.tool_id: [] for label in labels
        }

        for label in labels:
            tool_labels[label.tool_id].append(label.label_name)

        return tool_labels
