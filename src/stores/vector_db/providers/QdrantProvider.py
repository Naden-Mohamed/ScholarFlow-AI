import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ..VectorDBEnums import DistanceMetric
from ..VectorDBInterface import VectorDBInterface


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, url: str, distance_metric: str = "Cosine"):
        self.url = url
        self.client = None

        if distance_metric == DistanceMetric.COSINE.value:
            self.distance_metric = Distance.COSINE
        elif distance_metric == DistanceMetric.EUCLIDEAN.value:
            self.distance_metric = Distance.EUCLID
        elif distance_metric == DistanceMetric.DOT_PRODUCT.value:
            self.distance_metric = Distance.DOT
        else:
            self.distance_metric = Distance.COSINE

        self.logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self.client = QdrantClient(url=self.url)
            self.logger.info("Connected to Qdrant database.")
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant database: {e}")
            self.client = None

    def disconnect(self):
        if self.client:
            self.client = None
            self.logger.info("Disconnected from Qdrant database.")
        else:
            self.logger.warning(
                "No active connection to disconnect from Qdrant database."
            )

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return False

        if self.is_collection_exists(collection_name):
            if do_reset:
                self.client.delete_collection(collection_name)
                self.logger.info(f"Collection '{collection_name}' deleted for reset.")
            else:
                self.logger.info(
                    f"Collection '{collection_name}' already exists, skipping creation."
                )
                return True

        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=embedding_size, distance=self.distance_metric
                ),
            )
            self.logger.info(
                f"Collection '{collection_name}' created with size {embedding_size}."
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to create collection '{collection_name}': {e}")
            return False

    def is_collection_exists(self, collection_name: str) -> bool:
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return False
        try:
            return self.client.collection_exists(collection_name="{collection_name}")
        except Exception as e:
            self.logger.error(
                f"Failed to check if collection '{collection_name}' exists: {e}"
            )
            return False

    def delete_collection(self, collection_name: str):
        if self.client and self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name="{collection_name}")

    def get_collection_info(self, collection_name: str):
        if self.client:
            return self.client.get_collection(collection_name=collection_name)

    def list_all_collections(self):
        if self.client:
            return self.client.get_collections()

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        record_id: str | None = None,
        metadata: dict | None = None,
    ):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return False

        if record_id is None:
            record_id = str(uuid.uuid4())

        try:
            self.client.upsert(
                collection_name=collection_name,
                wait=True,
                points=[
                    PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, **(metadata or {})},
                    )
                ],
            )
            self.logger.info(
                f"Inserted one point into collection '{collection_name}' successfully."
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to insert point into collection '{collection_name}': {e}"
            )
            return False

    def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadatas: list | None = None,
        record_ids: list[str] | None = None,
        batch_size: int = 50,
    ):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return False

        if metadatas is None:
            metadatas = [{}] * len(texts)

        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_points = [
                PointStruct(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x], "metadata": batch_metadatas[x]},
                )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points,
                )
                self.logger.info(
                    f"Inserted batch of {len(batch_texts)} points into '{collection_name}'."
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to insert batch into '{collection_name}': {e}"
                )
                return False

        return True

    def search_by_vector(self, collection_name: str, vector: list, top_k: int = 3):
        if not self.client:
            self.logger.error("Qdrant client is not connected. Call connect() first.")
            return None

        try:
            search_result = self.client.query_points(
                collection_name=collection_name, query=vector, limit=top_k
            )
            self.logger.info(f"Search in '{collection_name}' completed successfully.")
            return search_result.points
            # the query_points method returns a QueryResponse object, not just a list.
            # You should ensure you are returning the .points attribute, which contains the actual search hits.
        except Exception as e:
            self.logger.error(f"Failed to search in '{collection_name}': {e}")
            return None
