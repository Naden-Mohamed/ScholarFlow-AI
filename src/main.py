from fastapi import FastAPI
from routers import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from models.db_schemas.data_chunk import DataChunk
import gridfs
import os

app = FastAPI()


settings = get_settings()
db_client = AsyncIOMotorClient(settings.MONGODB_URI)
db_name = db_client[settings.MONGODB_DB_NAME]
# fs = gridfs.GridFSBucket(db_name)

async def startup_span():
    app.mongodb_client = db_client
    app.mongodb = db_name
    # app.gridfs = fs
    # print("Connected to the MongoDB database!")
    try:
        await app.mongodb_client.admin.command("ping")
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")  # This will show the real error
        raise e  # Re-raise the exception to prevent the app from starting if the database connection fails

async def shutdown_span():
    app.mongodb_client.close()
    print("Disconnected from the MongoDB database!")
    # app.vector_db_client.disconnect() 


app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)
app.include_router(base.router)
app.include_router(data.data_router)
