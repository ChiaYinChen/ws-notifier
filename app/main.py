"""Main app."""
import asyncio

from fastapi import FastAPI

from .endpoint import router
from .handler import room_manager
from .middleware import RoomEventMiddleware
from .setting import settings

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)


@app.on_event("startup")
async def subscribe():
    if settings.TESTING is False:
        asyncio.create_task(room_manager.consume())

app.add_middleware(RoomEventMiddleware)
app.include_router(router)
