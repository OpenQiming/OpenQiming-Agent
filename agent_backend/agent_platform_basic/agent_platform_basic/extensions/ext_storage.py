from collections.abc import Generator
from typing import Union

from fastapi import FastAPI
from flask import Flask

from agent_platform_basic.extensions.storage.async_local_storage import AsyncLocalStorage
from agent_platform_basic.extensions.storage.async_s3_storage import AsyncS3Storage
from agent_platform_basic.extensions.storage.local_storage import LocalStorage
from agent_platform_basic.extensions.storage.s3_storage import S3Storage


class Storage:
    def __init__(self):
        self.storage_runner = None

    def init_app(self, app: Flask):
        storage_type = app.config.get('STORAGE_TYPE')
        if storage_type == 's3':
            self.storage_runner = S3Storage(
                app=app
            )
        else:
            self.storage_runner = LocalStorage(app=app)

    def save(self, filename, data):
        self.storage_runner.save(filename, data)

    def load(self, filename: str, stream: bool = False) -> Union[bytes, Generator]:
        if stream:
            return self.load_stream(filename)
        else:
            return self.load_once(filename)

    def load_once(self, filename: str) -> bytes:
        return self.storage_runner.load_once(filename)

    def load_stream(self, filename: str) -> Generator:
        return self.storage_runner.load_stream(filename)

    def download(self, filename, target_filepath):
        self.storage_runner.download(filename, target_filepath)

    def exists(self, filename):
        return self.storage_runner.exists(filename)

    def delete(self, filename):
        return self.storage_runner.delete(filename)


class AsyncStorage:
    def __init__(self):
        self.storage_runner = None

    def init_app(self, app: FastAPI):
        storage_type = app.state.config.get('STORAGE_TYPE')
        if storage_type == 's3':
            self.storage_runner = AsyncS3Storage(
                app=app
            )
        else:
            self.storage_runner = AsyncLocalStorage(app=app)

    async def save(self, filename, data):
        await self.storage_runner.save(filename, data)

    async def load(self, filename: str, stream: bool = False) -> Union[bytes, Generator]:
        if stream:
            return await self.load_stream(filename)
        else:
            return await self.load_once(filename)

    async def load_once(self, filename: str) -> bytes:
        return await self.storage_runner.load_once(filename)

    async def load_stream(self, filename: str) -> Generator:
        return await self.storage_runner.load_stream(filename)

    async def download(self, filename, target_filepath):
        await self.storage_runner.download(filename, target_filepath)

    async def exists(self, filename):
        return await self.storage_runner.exists(filename)

    async def delete(self, filename):
        return await self.storage_runner.delete(filename)


storage = Storage()
async_storage = AsyncStorage()


def init_app(app: Flask):
    storage.init_app(app)


def init_fastapi(app: FastAPI):
    async_storage.init_app(app)
