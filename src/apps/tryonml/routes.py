from src.utilities.route_builder import build_router
from src.apps.tryonml.schemas import DataSchema
from src.apps.tryonml.services.pipeline import VHDMService

model_router = build_router(path="models", tags=["AI-Model"])

@model_router.post("")
async def upload(dto: DataSchema):
    return await VHDMService.run(dto)
