from abc import ABC, abstractmethod


class AsyncEmbeddings(ABC):
    """Interface for embedding models."""

    @abstractmethod
    async def async_embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed search docs."""

    @abstractmethod
    async def async_embed_query(self, text: str) -> list[float]:
        """Embed query text."""
