from enum import Enum

class VectorDBType(Enum):
    QDRANT = "QDRANT"

class DistanceMetric(Enum):
    COSINE = "COSINE" # Measures the angle between vectors, focusing on orientation rather than magnitude
    EUCLIDEAN = "EUCLIDEAN" # Measures straight-line distance between points in space
    DOT_PRODUCT = "DOT_PRODUCT" # Measures the dot product of vectors, capturing both magnitude and direction
