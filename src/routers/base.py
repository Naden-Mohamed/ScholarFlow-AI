from fastapi import APIRouter, Depends
from ..helpers.config import Settings, get_settings


router = APIRouter(
    prefix="/api",
    tags=["api"]
)

@router.get("/")
def get_status(app_settings: Settings = Depends(get_settings)):
    return {"APP_NAME": app_settings.app_name}


@router.get("/health")
def health_check():
    return {"status": "ok"} 