from fastapi import FastAPI

from apps.api.routes.chat import router as chat_router
from apps.api.routes.health import router as health_router


app = FastAPI(
    title="Enterprise Agent Platform",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(chat_router)
