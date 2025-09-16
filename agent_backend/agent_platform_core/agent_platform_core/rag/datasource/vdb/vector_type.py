from enum import Enum


class VectorType(str, Enum):
    MILVUS = 'milvus'
    PGVECTOR = 'pgvector'
    PGVECTO_RS = 'pgvecto-rs'
    RELYT = 'relyt'
    TIDB_VECTOR = 'tidb_vector'
    WEAVIATE = 'weaviate'
