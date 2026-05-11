from enum import Enum

class VectorDBType(Enum):
    QDRANT = "QDRANT"

class DistanceMetric(Enum):
    COSINE = "Cosine" # Measures the angle between vectors, focusing on orientation rather than magnitude
    EUCLIDEAN = "Euclid" # Measures straight-line distance between points in space
    DOT_PRODUCT = "Dot" # Measures the dot product of vectors, capturing both magnitude and direction
