from fastapi import FastAPI

from src.api.errors import register_exception_handlers
from src.api.routes.chat import router as chat_router
from src.api.routes.health import router as health_router

app = FastAPI(title="IT Support System API", version="0.1.0")

register_exception_handlers(app)
app.include_router(chat_router)
app.include_router(health_router)
