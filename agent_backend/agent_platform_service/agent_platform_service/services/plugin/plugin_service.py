import logging
from collections.abc import Mapping, Sequence
from mimetypes import guess_type
from typing import Optional

from agent_platform_core.plugin.impl.asset import PluginAssetManager
from pydantic import BaseModel

from agent_platform_common.configs import agent_platform_config
from agent_platform_core.plugin.impl.plugin import PluginInstaller
from agent_platform_core.plugin.entities.plugin import (
    GenericProviderID,
    PluginDeclaration,
    PluginEntity,
    PluginInstallation,
    PluginInstallationSource,
)

from agent_platform_core.plugin.entities.plugin_daemon import (
    PluginDecodeResponse,
    PluginInstallTask,
    PluginListResponse,
    PluginVerification,
)

from agent_platform_service.services.feature_service import FeatureService, PluginInstallationScope
from agent_platform_service.services.errors.plugin import PluginInstallationForbiddenError
from agent_platform_core.plugin.impl.debugging import PluginDebuggingClient
from agent_platform_basic.extensions.ext_redis import redis_client

class PluginService:
    @staticmethod
    def upload_pkg(tenant_id: str, pkg: bytes, verify_signature: bool = False) -> PluginDecodeResponse:
        """
        Upload plugin package files

        returns: plugin_unique_identifier
        """
        PluginService._check_marketplace_only_permission()
        manager = PluginInstaller()
        features = FeatureService.get_system_features()
        response = manager.upload_pkg(
            tenant_id,
            pkg,
            verify_signature=features.plugin_installation_permission.restrict_to_marketplace_only,
        )
        return response

    @staticmethod
    def install_from_local_pkg(tenant_id: str, plugin_unique_identifiers: Sequence[str]):
        PluginService._check_marketplace_only_permission()
        manager = PluginInstaller()

        return manager.install_from_identifiers(
            tenant_id,
            plugin_unique_identifiers,
            PluginInstallationSource.Package,
            [{}],
        )

    @staticmethod
    def _check_marketplace_only_permission():
        """
        Check if the marketplace only permission is enabled
        """
        features = FeatureService.get_system_features()
        if features.plugin_installation_permission.restrict_to_marketplace_only:
            raise PluginInstallationForbiddenError("Plugin installation is restricted to marketplace only")

    @staticmethod
    def fetch_install_tasks(tenant_id: str, page: int, page_size: int) -> Sequence[PluginInstallTask]:
        """
        Fetch plugin installation tasks
        """
        manager = PluginInstaller()
        return manager.fetch_plugin_installation_tasks(tenant_id, page, page_size)

    @staticmethod
    def fetch_install_task(tenant_id: str, task_id: str) -> PluginInstallTask:
        manager = PluginInstaller()
        return manager.fetch_plugin_installation_task(tenant_id, task_id)

    @staticmethod
    def delete_install_task(tenant_id: str, task_id: str) -> bool:
        """
        Delete a plugin installation task
        """
        manager = PluginInstaller()
        return manager.delete_plugin_installation_task(tenant_id, task_id)

    @staticmethod
    def delete_install_task_item(tenant_id: str, task_id: str, identifier: str) -> bool:
        """
        Delete a plugin installation task item
        """
        manager = PluginInstaller()
        return manager.delete_plugin_installation_task_item(tenant_id, task_id, identifier)

    @staticmethod
    def uninstall(tenant_id: str, plugin_installation_id: str) -> bool:
        manager = PluginInstaller()
        return manager.uninstall(tenant_id, plugin_installation_id)

    @staticmethod
    def list_installations_from_ids(tenant_id: str, ids: Sequence[str]) -> Sequence[PluginInstallation]:
        """
        List plugin installations from ids
        """
        manager = PluginInstaller()
        return manager.fetch_plugin_installation_by_ids(tenant_id, ids)

    @staticmethod
    def get_asset(tenant_id: str, asset_file: str) -> tuple[bytes, str]:
        """
        get the asset file of the plugin
        """
        manager = PluginAssetManager()
        # guess mime type
        mime_type, _ = guess_type(asset_file)
        return manager.fetch_asset(tenant_id, asset_file), mime_type or "application/octet-stream"

    @staticmethod
    def list_with_total(tenant_id: str, page: int, page_size: int) -> PluginListResponse:
        """
        list all plugins of the tenant
        """
        manager = PluginInstaller()
        plugins = manager.list_plugins_with_total(tenant_id, page, page_size)
        return plugins

    @staticmethod
    def get_debugging_key(tenant_id: str) -> str:
        """
        get the debugging key of the tenant
        """
        manager = PluginDebuggingClient()
        return manager.get_debugging_key(tenant_id)

    @staticmethod
    def fetch_plugin_manifest(tenant_id: str, plugin_unique_identifier: str) -> PluginDeclaration:
        """
        Fetch plugin manifest
        """
        manager = PluginInstaller()
        return manager.fetch_plugin_manifest(tenant_id, plugin_unique_identifier)