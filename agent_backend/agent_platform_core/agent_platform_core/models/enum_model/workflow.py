from enum import Enum, StrEnum

from typing import Union



"""
@Date    ：2024/7/15 10:02 
@Version: 1.0
@Description:

"""


class WorkflowType(Enum):
    """
    Workflow Type Enum
    """

    WORKFLOW = "workflow"
    CHAT = "chat"

    @classmethod
    def value_of(cls, value: str) -> "WorkflowType":
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"invalid workflow type value {value}")

    @classmethod
    def from_app_mode(cls, app_mode: Union[str, "AppMode"]) -> "WorkflowType":
        """
        Get workflow type from app mode.

        :param app_mode: app mode
        :return: workflow type
        """
        from agent_platform_core.models.enum_model.app_mode import AppMode

        app_mode = app_mode if isinstance(app_mode, AppMode) else AppMode.value_of(app_mode)
        return cls.WORKFLOW if app_mode == AppMode.WORKFLOW else cls.CHAT


class WorkflowRunTriggeredFrom(StrEnum):
    DEBUGGING = "debugging"
    APP_RUN = "app-run"


class WorkflowRunStatus(StrEnum):
    """
    Workflow Run Status Enum
    """

    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    STOPPED = "stopped"

    @classmethod
    def value_of(cls, value: str) -> "WorkflowRunStatus":
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"invalid workflow run status value {value}")


class WorkflowNodeExecutionTriggeredFrom(Enum):
    """
    Workflow Node Execution Triggered From Enum
    """

    SINGLE_STEP = "single-step"
    WORKFLOW_RUN = "workflow-run"

    @classmethod
    def value_of(cls, value: str) -> "WorkflowNodeExecutionTriggeredFrom":
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"invalid workflow node execution triggered from value {value}")


class WorkflowNodeExecutionStatus(Enum):
    """
    Workflow Node Execution Status Enum
    """

    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXCEPTION = "exception"
    RETRY = "retry"

    @classmethod
    def value_of(cls, value: str) -> "WorkflowNodeExecutionStatus":
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"invalid workflow node execution status value {value}")


class WorkflowAppLogCreatedFrom(Enum):
    """
    Workflow App Log Created From Enum
    """

    SERVICE_API = "service-api"
    WEB_APP = "web-app"
    INSTALLED_APP = "installed-app"

    @classmethod
    def value_of(cls, value: str) -> "WorkflowAppLogCreatedFrom":
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"invalid workflow app log created from value {value}")
