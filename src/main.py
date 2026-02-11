from fastapi import FastAPI
from routers import base, data

app = FastAPI()

app.include_router(base.router)
app.include_router(data.data_router)
