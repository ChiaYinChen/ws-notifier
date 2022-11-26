"""Service."""
import json

from .handler import RoomManager
from .setting import settings


async def publish_channel_message(room: RoomManager, type: str, message: str, **extra_params):
    """Publish a message to channel."""
    if settings.TESTING:
        return
    params = {"type": type, "message": message}
    params.update(extra_params)
    await room.publish(
        "channel",
        json.dumps(params)
    )
