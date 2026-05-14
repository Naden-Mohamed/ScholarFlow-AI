from stores.vector_db.providers.QdrantProvider import QdrantDBProvider
from .VectorDBEnums import VectorDBType

class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        if provider == VectorDBType.QDRANT.value:
            return QdrantDBProvider(
                url=self.config.QDRANT_URL,
                api_key=self.config.QDRANT_API_KEY,
                distance_metric=self.config.VECTOR_DB_DISTANCE_METRIC
            )
        
        return None