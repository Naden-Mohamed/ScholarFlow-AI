from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBType as VectorDBEnums
from stores.vector_db import VectorDBEnums

class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            return QdrantDBProvider(
                url=self.config.VECTOR_DB_URL,
                api_key=self.config.VECTOR_DB_API_KEY,
                distance_metric=self.config.VECTOR_DB_DISTANCE_METRIC
            )
        
        return None