from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import base, data, rag
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from .stores import LLMProviderFactory
from .stores import VectorDBProviderFactory
from .stores.llm.templates.template_parser import TemplateParser
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.mongodb = app.mongodb_client[settings.MONGODB_DB_NAME]
    try:
        await app.mongodb_client.admin.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")  
        raise e  

    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(settings)

    app.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()  
    print("Connected to the Qdrant Vector database!")

    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                                embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    app.template_parser = TemplateParser(
    language=settings.PRIMARY_LANG,
    default_language=settings.DEFAULT_LANG,
    )

  

    yield

    app.mongodb_client.close()
    print("Disconnected from the MongoDB database!")
    app.vector_db_client.disconnect()
    print("Disconnected from the Qdrant Vector database!")


app = FastAPI(lifespan=lifespan)

app.include_router(base.router)
app.include_router(data.data_router)
app.include_router(rag.rag_router)