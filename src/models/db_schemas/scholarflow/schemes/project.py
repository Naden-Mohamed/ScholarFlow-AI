import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .scholarflow_base import SQLAlchemyBase


class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True)
    project_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    chunks = relationship("DataChunk", back_populates="project")
    assets = relationship("Asset", back_populates="project")
