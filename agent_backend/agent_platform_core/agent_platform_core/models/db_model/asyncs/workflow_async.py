import json
from hashlib import sha256

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.models.db_model import Account
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.libs import helper
from typing import Any
import asyncio
from collections.abc import Sequence
from agent_platform_core import contexts
from agent_platform_common.constants import HIDDEN_VALUE
from agent_platform_core.variables import (
    SecretVariable,
    Variable,
)
# from agent_platform_core.factories import factory
from agent_platform_core.helper import encrypter


class WorkflowAsync:
    def __init__(self, session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

        # origin_environment_variables = self.environment_variables(tenant_id)

    async def environment_variable_encrypt_async(self, value: Sequence[Variable], origin_environment_variables, tenant_id):

        value = list(value)
        if any(var for var in value if not var.id):
            raise ValueError('environment variable require a unique id')

        # Compare inputs and origin variables, if the value is HIDDEN_VALUE, use the origin variable value (only update `name`).
        origin_variables_dictionary = {var.id: var for var in origin_environment_variables}
        for i, variable in enumerate(value):
            if variable.id in origin_variables_dictionary and variable.value == HIDDEN_VALUE:
                value[i] = origin_variables_dictionary[variable.id].model_copy(update={'name': variable.name})

        async def encrypt_func(var):
            if isinstance(var, SecretVariable):
                encrypted_value = await encrypter.encrypt_token_async(self.session, tenant_id=tenant_id, token=var.value)
                return var.model_copy(update={'value': encrypted_value})
            return var

        # Await all asynchronous encrypt_func calls concurrently
        encrypted_vars = await asyncio.gather(*[encrypt_func(var) for var in value])
        return encrypted_vars

