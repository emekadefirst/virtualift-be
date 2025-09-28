from src.apps.file import file_router
from src.apps.tryonml.routes import model_router
from src.apps.auth.routes.user_routes import user_router

routes = [
   user_router,
   file_router, 
   model_router
]