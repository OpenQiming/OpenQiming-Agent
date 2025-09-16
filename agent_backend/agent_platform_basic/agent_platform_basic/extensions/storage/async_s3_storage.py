from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from aiobotocore.session import AioSession
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI

from agent_platform_basic.extensions.storage.async_base_storage import AsyncBaseStorage


class AsyncS3Storage(AsyncBaseStorage):
    """Implementation for S3 storage."""

    def __init__(self, app: FastAPI):
        super().__init__(app)
        app_config = self.app_config
        self.bucket_name = app_config.get('S3_BUCKET_NAME')
        self.session = AioSession()
        if app_config.get('S3_USE_AWS_MANAGED_IAM'):
            self.client_config = {'service_name': 's3'}
        else:
            self.client_config = {
                'service_name': 's3',
                'aws_secret_access_key': app_config.get('S3_SECRET_KEY'),
                'aws_access_key_id': app_config.get('S3_ACCESS_KEY'),
                'endpoint_url': app_config.get('S3_ENDPOINT'),
                'region_name': app_config.get('S3_REGION'),
                'config': Config(s3={'addressing_style': app_config.get('S3_ADDRESS_STYLE')})
            }

    @asynccontextmanager
    async def _get_client(self):
        async with self.session.create_client(**self.client_config) as client:
            yield client

    async def save(self, filename, data):
        async with self._get_client() as client:
            await client.put_object(Bucket=self.bucket_name, Key=filename, Body=data)

    async def load_once(self, filename: str) -> bytes:
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=filename)
                return await response['Body'].read()
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError("File not found")
            else:
                raise

    async def load_stream(self, filename: str) -> AsyncGenerator:
        async with self._get_client() as client:
            try:
                response = await client.get_object(Bucket=self.bucket_name, Key=filename)
                async for chunk in response['Body'].iter_chunks():
                    yield chunk
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'NoSuchKey':
                    raise FileNotFoundError("File not found")
                else:
                    raise

    async def download(self, filename, target_filepath):
        async with self._get_client() as client:
            await client.download_file(self.bucket_name, filename, target_filepath)

    async def exists(self, filename):
        async with self._get_client() as client:
            try:
                await client.head_object(Bucket=self.bucket_name, Key=filename)
                return True
            except ClientError:
                return False

    async def delete(self, filename):
        async with self._get_client() as client:
            await client.delete_object(Bucket=self.bucket_name, Key=filename)
