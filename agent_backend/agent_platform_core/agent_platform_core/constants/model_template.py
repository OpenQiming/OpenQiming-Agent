import json

from ..models.enum_model.app_mode import AppMode

default_app_templates = {
    # workflow default mode
    AppMode.WORKFLOW: {
        "app": {
            "mode": AppMode.WORKFLOW.value,
            "enable_site": True,
            "enable_api": True,
        }
    },
    # metabolic default mode
    AppMode.METABOLIC: {
        "app": {
            "mode": AppMode.METABOLIC.value,
            "enable_site": True,
            "enable_api": True
        }
    },
    # completion default mode
    AppMode.COMPLETION: {
        "app": {
            "mode": AppMode.COMPLETION.value,
            "enable_site": True,
            "enable_api": True,
        },
        "model_config": {
            "model": {
                "provider": "openai",
                "name": "gpt-4o",
                "mode": "chat",
                "completion_params": {},
            },
            "user_input_form": json.dumps(
                [
                    {
                        "paragraph": {
                            "label": "Query",
                            "variable": "query",
                            "required": True,
                            "default": "",
                        },
                    },
                ]
            ),
            "pre_prompt": "{{query}}",
        },
    },
    # chat default mode
    AppMode.CHAT: {
        "app": {
            "mode": AppMode.CHAT.value,
            "enable_site": True,
            "enable_api": True,
        },
        "model_config": {
            "model": {
                "provider": "openai",
                "name": "gpt-4o",
                "mode": "chat",
                "completion_params": {},
            },
        },
    },
    # advanced-chat default mode
    AppMode.ADVANCED_CHAT: {
        "app": {
            "mode": AppMode.ADVANCED_CHAT.value,
            "enable_site": True,
            "enable_api": True,
        },
    },
    # agent-chat default mode
    AppMode.AGENT_CHAT: {
        "app": {
            "mode": AppMode.AGENT_CHAT.value,
            "enable_site": True,
            "enable_api": True,
        },
        "model_config": {
            "model": {
                "provider": "openai",
                "name": "gpt-4o",
                "mode": "chat",
                "completion_params": {},
            },
        },
    },
}
