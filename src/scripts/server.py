import uvicorn
from src.core.routes import routes
from fastapi import FastAPI, responses
from src.core.database import TORTOISE_ORM
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from src.apps.tryonml.services.pipeline import VHDMService

app = FastAPI(
    title="Vitual Fit API",
    description="This is the api for Virtual Fit",
    version="1.0.0",
    contact={
        "name": "Vitual Fit API",
        "url": "https://virtualfite.ai/support",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/license/mit/"
    },
    default_response_class=responses.ORJSONResponse,
)
# @app.on_event("startup")
# async def startup_event():
#     await VHDMService.init()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

list(map(lambda r: app.include_router(r), routes))

def run_server():
    uvicorn.run("src.scripts.server:app", host="0.0.0.0", port=8080, reload=True)


# def run_prod():
#     uvicorn.run("src.scripts.server:app", host="0.0.0.0", port=8080, reload=False, workers=1)