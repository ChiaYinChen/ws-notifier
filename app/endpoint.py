"""Endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from starlette.endpoints import WebSocketEndpoint

from .const import WSAction
from .deps import get_current_room
from .handler import RoomManager
from .service import publish_channel_message

router = APIRouter()


@router.post("/send-message")
async def send_message(
    event_id: str,
    client_id: str,
    room: RoomManager = Depends(get_current_room)
):
    """Broadcast a message to a specific event of clients."""
    try:
        await publish_channel_message(
            room=room,
            type=WSAction.GROUP.value,
            message=f"{event_id} group message",
            event_id=event_id,
        )
        await publish_channel_message(
            room=room,
            type=WSAction.PERSONAL.value,
            message=f"{event_id}:{client_id} innnnnnnnnn",
            event_id=event_id,
            client_id=client_id
        )
    except ValueError:
        raise HTTPException(404, detail=f"No such event: {event_id}")


@router.websocket_route("/ws/{event_id}/{client_id}", name="ws")
class RoomLive(WebSocketEndpoint):
    """Live connection to the global :class:`~.RoomManager` instance, via WebSocket."""

    encoding: str = "text"

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)
        self.room: RoomManager | None = None
        self.event_id: str | None = args[0]["path_params"].get("event_id")
        self.client_id: str | None = args[0]["path_params"].get("client_id")

    async def on_connect(self, websocket):
        """
        Handle a new connection.
        New user is added to the global :class:`~.RoomManager` instance.
        """
        room: RoomManager | None = self.scope.get("room")
        if room is None:
            raise RuntimeError("Global `RoomManager` instance unavailable!")
        self.room = room
        await self.room.connect(self.event_id, self.client_id, websocket)

    async def on_disconnect(self, websocket, close_code):
        """
        Disconnect the user, removing them from the :class:`~.RoomManager`.
        """
        self.room.disconnect(self.event_id, self.client_id, websocket)
