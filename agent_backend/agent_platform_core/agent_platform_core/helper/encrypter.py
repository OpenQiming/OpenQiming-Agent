import base64

from agent_platform_basic.extensions.ext_database import db, async_db
from sqlalchemy import select
from agent_platform_basic.libs import rsa


def obfuscated_token(token: str):
    if not token:
        return token
    if len(token) <= 8:
        return "*" * 20
    return token[:6] + "*" * 12 + token[-2:]


def encrypt_token(tenant_id: str, token: str):
    from agent_platform_basic.models.db_model import Tenant

    if not (tenant := db.session.query(Tenant).filter(Tenant.id == tenant_id).first()):
        raise ValueError(f"Tenant with id {tenant_id} not found")
    encrypted_token = rsa.encrypt(token, tenant.encrypt_public_key)
    return base64.b64encode(encrypted_token).decode()


async def encrypt_token_async(session, tenant_id: str, token: str):
    from agent_platform_basic.models.db_model import Tenant

    tenant_scaler = await session.execute(select(Tenant).filter(Tenant.id == tenant_id))
    tenant = tenant_scaler.scalar_one_or_none()
    if not tenant:
        raise ValueError(f"Tenant with id {tenant_id} not found")
    encrypted_token = rsa.encrypt(token, tenant.encrypt_public_key)
    return base64.b64encode(encrypted_token).decode()


def decrypt_token(tenant_id: str, token: str):
    return rsa.decrypt(base64.b64decode(token), tenant_id)


async def async_decrypt_token(tenant_id: str, token: str):
    return await rsa.async_decrypt(base64.b64decode(token), tenant_id)


def batch_decrypt_token(tenant_id: str, tokens: list[str]):
    rsa_key, cipher_rsa = rsa.get_decrypt_decoding(tenant_id)

    return [rsa.decrypt_token_with_decoding(base64.b64decode(token), rsa_key, cipher_rsa) for token in tokens]


def get_decrypt_decoding(tenant_id: str):
    return rsa.get_decrypt_decoding(tenant_id)


async def async_get_decrypt_decoding(tenant_id: str):
    return await rsa.async_get_decrypt_decoding(tenant_id)


def decrypt_token_with_decoding(token: str, rsa_key, cipher_rsa):
    return rsa.decrypt_token_with_decoding(base64.b64decode(token), rsa_key, cipher_rsa)
