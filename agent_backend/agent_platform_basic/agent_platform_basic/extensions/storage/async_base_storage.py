"""Abstract interface for file storage implementations."""
from abc import ABC, abstractmethod
from collections.abc import Generator

from fastapi import FastAPI


class AsyncBaseStorage(ABC):
    """Interface for file storage.
    """
    app = None

    def __init__(self, app: FastAPI):
        self.app_config = app.state.config

    @abstractmethod
    async def save(self, filename, data):
        raise NotImplementedError

    @abstractmethod
    async def load_once(self, filename: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def load_stream(self, filename: str) -> Generator:
        raise NotImplementedError

    @abstractmethod
    async def download(self, filename, target_filepath):
        raise NotImplementedError

    @abstractmethod
    async def exists(self, filename):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, filename):
        raise NotImplementedError
