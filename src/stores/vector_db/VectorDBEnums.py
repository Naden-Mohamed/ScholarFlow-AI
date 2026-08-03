from enum import Enum

class VectorDBType(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"

class DistanceMetric(Enum):
    COSINE = "Cosine" # Measures the angle between vectors, focusing on orientation rather than magnitude
    EUCLIDEAN = "Euclid" # Measures straight-line distance between points in space
    DOT_PRODUCT = "Dot" # Measures the dot product of vectors, capturing both magnitude and direction

class PgVectorTableSchemeEnums(Enum):
    ID = 'id'
    TEXT = 'text'
    VECTOR = 'vector'
    CHUNK_ID = 'chunk_id'
    METADATA = 'metadata'
    _PREFIX = 'pgvector'

class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PgVectorIndexTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"