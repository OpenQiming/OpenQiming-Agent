from typing import Any

from agent_platform_core.tools.errors import ToolProviderCredentialValidationError
from agent_platform_core.tools.provider.builtin.time.tools.current_time import CurrentTimeTool
from agent_platform_core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class WikiPediaProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            CurrentTimeTool().invoke(
                user_id="",
                tool_parameters={},
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
