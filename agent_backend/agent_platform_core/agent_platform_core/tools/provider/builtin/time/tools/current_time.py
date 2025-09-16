from datetime import UTC, datetime
from typing import Any, Union

from pytz import timezone as pytz_timezone

from agent_platform_core.tools.entities.tool_entities import ToolInvokeMessage
from agent_platform_core.tools.tool.builtin_tool import BuiltinTool


class CurrentTimeTool(BuiltinTool):
    def _invoke(
        self,
        user_id: str,
        tool_parameters: dict[str, Any],
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        invoke tools
        """
        # get timezone
        tz = tool_parameters.get("timezone", "Asia/Shanghai")
        fm = tool_parameters.get("format") or "%Y-%m-%d %H:%M:%S %Z"
        if tz == "UTC":
            return self.create_text_message(f"{datetime.now(UTC).strftime(fm)}")

        try:
            tz = pytz_timezone(tz)
        except:
            return self.create_text_message(f"Invalid timezone: {tz}")
        return self.create_text_message(f"{datetime.now(tz).strftime(fm)}")

    async def _async_invoke(
        self, user_id: str, tool_parameters: dict[str, Any]
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        return self._invoke(user_id, tool_parameters)