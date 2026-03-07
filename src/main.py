from fastapi import FastAPI
from routers import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from .stores.llm.LLMProviderFactory import LLMProviderFactory
import os

app = FastAPI()

settings = get_settings()
db_client = AsyncIOMotorClient(settings.MONGODB_URI)
db_name = db_client[settings.MONGODB_DB_NAME]


async def startup_span():
    app.mongodb_client = db_client
    app.mongodb = db_name
    try:
        await app.mongodb_client.admin.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")  
        raise e  

    llm_provider_factory = LLMProviderFactory(config=settings)


    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                                embedding_size=settings.EMBEDDING_MODEL_SIZE)
async def shutdown_span():
    app.mongodb_client.close()
    print("Disconnected from the MongoDB database!")


app.router.lifespan.on_startup.append(startup_span)
app.router.lifespan.on_shutdown.append(shutdown_span)

app.include_router(base.router)
app.include_router(data.data_router)
