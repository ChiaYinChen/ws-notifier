"""Middleware."""
from starlette.types import ASGIApp, Receive, Scope, Send

from .handler import room_manager


class RoomEventMiddleware:
    """
    Middleware for providing a global :class:`~.RoomManager` instance
    to both HTTP and WebSocket scopes.
    """

    def __init__(self, app: ASGIApp):
        self._app = app
        self._room = room_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ("lifespan", "http", "websocket"):
            scope["room"] = self._room
        await self._app(scope, receive, send)
