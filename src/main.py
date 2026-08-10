from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import data, base, rag
from utils.metrics import setup_metrics
from helpers.bootstrap import build_clients

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize and assign clients to app.state
    (
        app.state.db_engine,
        app.state.db_client,
        app.state.generation_client,
        app.state.embedding_client,
        app.state.vectordb_client,
        app.state.template_parser,
    ) = await build_clients()
    
    yield
    
    # Shutdown: Clean up connections
    await app.state.db_engine.dispose()
    await app.state.vectordb_client.disconnect()

app = FastAPI(lifespan=lifespan)
setup_metrics(app)

app.include_router(base.router)
app.include_router(data.data_router)
app.include_router(rag.rag_router)