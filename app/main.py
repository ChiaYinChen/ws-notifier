"""Main app."""
import asyncio

from fastapi import FastAPI

from .endpoint import router
from .handler import room_manager
from .middleware import RoomEventMiddleware
from .setting import settings

app = FastAPI()


@app.on_event("startup")
async def subscribe():
    if settings.TESTING is False:
        asyncio.create_task(room_manager.consume())

app.add_middleware(RoomEventMiddleware)
app.include_router(router)
