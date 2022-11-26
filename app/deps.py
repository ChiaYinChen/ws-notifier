"""Dependencies."""
from fastapi import HTTPException, Request

from .handler import RoomManager


async def get_current_room(request: Request):
    """Get current room."""
    room: RoomManager | None = request.get("room")
    if room is None:
        raise HTTPException(500, detail="Global `RoomManager` instance unavailable!")
    return room
