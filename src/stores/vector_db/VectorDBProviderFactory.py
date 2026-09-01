from sqlalchemy.orm import sessionmaker

from stores.vector_db import PGVectorProvider, QdrantDBProvider

from .VectorDBEnums import VectorDBType


class VectorDBProviderFactory:
    def __init__(self, config, db_client: sessionmaker | None = None):
        self.config = config
        self.db_client = db_client

    def create(self, provider: str):
        if provider == VectorDBType.QDRANT.value:
            return QdrantDBProvider(
                url=self.config.QDRANT_URL,
                distance_metric=self.config.VECTOR_DB_DISTANCE_METRIC,
            )

        if provider == VectorDBType.PGVECTOR.value:
            return PGVectorProvider(
                db_client=self.db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METRIC,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD,
            )

        return None
