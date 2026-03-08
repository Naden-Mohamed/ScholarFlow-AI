from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBType,DistanceMetric
from qdrant_client import models, QdrantClient
from typing import List
import logging
import os

class QdrantProvider(VectorDBInterface):
    def __init__(self, url:str, api_key:str, distance_metric:str = "Cosine"):
        self.url = url
        self.api_key = api_key
        self.distance_metric = None
        self.client = None

        if distance_metric == DistanceMetric.COSINE.value:
            self.distance_metric = DistanceMetric.COSINE.value
        elif distance_metric == DistanceMetric.EUCLIDEAN.value:
            self.distance_metric = DistanceMetric.EUCLIDEAN.value
        elif distance_metric == DistanceMetric.DOT_PRODUCT.value:
            self.distance_metric = DistanceMetric.DOT_PRODUCT.value

        self.logger = logging.getLogger(__name__)

    def conntect(self):
        try:
            self.client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
            self.logger.info(f"Connected to Qdrant database at '{self.db_path}'.")
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant database at '{self.db_path}': {e}")
            self.client = None
    def disconnect(self):
        if self.client:
            self.client = None
            self.logger.info("Disconnected from Qdrant database.")
        else:
            self.logger.warning("No active connection to disconnect from Qdrant database.")


    def create_collection(self, collection_name:str, embedding_size:int, do_reset:bool = False):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return

        if self.client.is_collection_exists(collection_name):
            if do_reset:
                self.client.delete_collection(collection_name)
                self.logger.info(f"Existing collection '{collection_name}' deleted for reset.")
            else:
                self.logger.warning(f"Collection '{collection_name}' already exists. Use do_reset=True to reset it.")
                return

        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            self.logger.info(f"Collection '{collection_name}' created successfully with embedding size {embedding_size} and distance metric '{self.distance_metric}'.")
        except Exception as e:
            self.logger.error(f"Failed to create collection '{collection_name}': {e}")


    def is_collection_exists(self, collection_name:str) -> bool:
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return False
        try:
            return self.client.collection_exists(collection_name)
        except Exception as e:
            self.logger.error(f"Failed to check if collection '{collection_name}' exists: {e}")
            return False
        
    def delete_collection(self, collection_name:str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def get_collection_info(self, collection_name):
        return self.client.get_collection(collection_name=collection_name)
    def list_all_collections(self):
        return self.client.get_collections()

    def insert_one(self, collection_name:str, text:str, vector:list, metadata:dict = None):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return

        try:
            self.client.upsert(
                collection_name=collection_name,
                # Points are the central entity that Qdrant operates with. A point is a record consisting of three components: an ID, a vector, and an optional payload.
                points=[
                    models.PointStruct(
                        id=None,  # Let Qdrant auto-generate the ID
                        vector=vector,
                        payload={
                            "text": text,
                            **(metadata or {})  # Merge text and metadata into the payload
                        }
                    )
                ]
            )
            self.logger.info(f"Inserted one point into collection '{collection_name}' successfully.")
        except Exception as e:
            self.logger.error(f"Failed to insert point into collection '{collection_name}': {e}")

    def insert_many(self, collection_name:str, texts:list, vectors:list, metadatas:list = None, batch_size:int = 50):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return
        if metadatas is None or len(metadatas) == 0:
            metadatas = [{}] * len(texts)  # Create empty metadata for each text if not provided

        try:
            points = []
            for i in range(0, len(texts), batch_size):
                batch_end = i + batch_size
                batch_texts = texts[i:batch_end]
                batch_vectors = vectors[i:batch_end]
                batch_metadatas = metadatas[i:batch_end]

                point = [
                    models.PointStruct(
                    id=None,  
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        **(batch_metadatas[x] if batch_metadatas else {}) 
                    }
                )
                for x in range(len(batch_texts)) 
                ]

            try:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=point
                    )
                    self.logger.info(f"Inserted batch of {len(batch_texts)} points into collection '{collection_name}' successfully.")
            except Exception as e:
                    self.logger.error(f"Failed to insert batch of points into collection '{collection_name}': {e}")

        except Exception as e:
            self.logger.error(f"Failed to insert points into collection '{collection_name}': {e}")

    def search_by_vector(self, collection_name:str, vector:list, top_k:int=5):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return

        try:
            search_result = self.client.query_points(
                collection_name=collection_name,
                query_vector=vector,
                limit=top_k
            )
            self.logger.info(f"Search in collection '{collection_name}' completed successfully.")
            return search_result
        except Exception as e:
            self.logger.error(f"Failed to search in collection '{collection_name}': {e}")
            return None