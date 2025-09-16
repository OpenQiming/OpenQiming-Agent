import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
import base64
import json

backend = default_backend()


def derive_key(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 确保密钥长度为 32 字节（256 位）
        salt=salt,
        iterations=100000,
        backend=backend
    )
    return kdf.derive(password)


def get_aes_secret():
    # todo 是否需要从配置或数据库读取
    return os.environ.get("AES_SECRET")


def encrypt_data_and_base64_encode(data: str):
    try:
        password = get_aes_secret()
        password_bytes = password.encode('utf-8')

        salt = os.urandom(16)
        key = derive_key(password_bytes, salt)

        serialized_data = json.dumps(data).encode('utf-8')
        encrypted_data = salt + encrypt_with_aes(serialized_data, key)

        encrypted_data_base64 = base64.b64encode(encrypted_data).decode('utf-8')
        return encrypted_data_base64
    except Exception as e:
        raise ValueError(f'encrypt_data_and_base64_encode error: {e}')


def decrypt_data_from_base64(encrypted_data_base64: str):
    try:
        encrypted_data = base64.b64decode(encrypted_data_base64)
        salt = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]

        password = get_aes_secret()
        password_bytes = password.encode('utf-8')

        key = derive_key(password_bytes, salt)
        decrypted_data = decrypt_with_aes(encrypted_data, key)
        return json.loads(decrypted_data.decode('utf-8'))
    except Exception as e:
        raise ValueError(f'decrypt_data_from_base64 error: {e}')


def encrypt_with_aes(data: bytes, key: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data


def decrypt_with_aes(encrypted_data: bytes, key: bytes) -> bytes:
    iv = encrypted_data[:16]
    actual_encrypted_data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(actual_encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data
