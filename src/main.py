import os
import asyncio 
from contextlib import asynccontextmanager

from fastapi import FastAPI
from routers import base, data, rag
from helpers.config import get_settings
from stores import LLMProviderFactory, VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.metrics import setup_metrics

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    postgres_conn = (
        f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    )

    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )

    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(settings)

    app.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    
    app.vector_db_client.connect()  
    print("Connected to the Qdrant Vector database!")

    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )
    
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

    yield  # The application runs while suspended here

  
    if hasattr(app, "vector_db_client"):
        app.vector_db_client.disconnect() 
        
    if hasattr(app, "db_engine"):
        await app.db_engine.dispose()


app = FastAPI(lifespan=lifespan)

setup_metrics(app) 

app.include_router(base.router)
app.include_router(data.data_router)
app.include_router(rag.rag_router)