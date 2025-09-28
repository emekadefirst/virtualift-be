from src.utilities.route_builder import build_router
from src.apps.tryonml.schemas import DataSchema
from src.apps.tryonml.services.pipeline import VHDMService
import traceback
from fastapi import HTTPException


model_router = build_router(path="models", tags=["AI-Model"])

@model_router.on_event("startup")
async def startup_event():
    try:
        await VHDMService.init()
    except Exception as e:
        print(f"Startup error: {str(e)}\n{traceback.format_exc()}")
        raise

@model_router.post("")
async def upload(dto: DataSchema):
    try:
        return await VHDMService.run(dto)
    except Exception as e:
        print(f"Upload error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")