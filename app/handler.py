"""Handler."""
import asyncio
import json
import logging
from collections import defaultdict

import aioredis
from fastapi import WebSocket

from .const import WSAction
from .setting import settings

logger = logging.getLogger(__name__)


class RoomManager:
    """Room state, comprising connected clients."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self._active_connections = defaultdict(dict)
        self._client = aioredis.from_url(
            settings.redis_dsn, db=1, encoding="utf-8", decode_responses=True)

    async def connect(self, event_id: str, client_id: str, websocket: WebSocket):
        """Create a websocket connection."""
        await websocket.accept()
        await websocket.send_json(
            {
                "type": WSAction.ROOM_JOIN.value,
                "data": {
                    "event_id": event_id,
                    "client_id": client_id
                }
            }
        )
        self.add_user(event_id, client_id, websocket)

    def add_user(self, event_id: str, client_id: str, websocket: WebSocket):
        """Add a user websocket, keyed by corresponding client ID."""
        if event_id not in self._active_connections:
            self._active_connections[event_id] = defaultdict(list)
        self._active_connections[event_id][client_id].append(websocket)

    def disconnect(self, event_id: str, client_id: str, websocket: WebSocket):
        """Disconnect a user from the room."""
        self._active_connections[event_id][client_id].remove(websocket)

    async def send_group_message(self, event_id: str, message: str):
        """Send a message to specific groups of clients."""
        if self._active_connections.get(event_id):
            for websockets in self._active_connections[event_id].values():
                for websocket in websockets:
                    try:
                        await websocket.send_json(
                            {
                                "type": WSAction.GROUP.value,
                                "message": message
                            }
                        )
                        print(f"sent to event {event_id} => {message}")
                    except Exception as exc:
                        logger.error(exc)

    async def send_personal_message(self, event_id: str, client_id: str, message: str):
        """Send a message to specific connected clients."""
        if self._active_connections.get(event_id, {}).get(client_id):
            for websocket in self._active_connections[event_id][client_id]:
                try:
                    await websocket.send_json(
                        {
                            "type": WSAction.PERSONAL.value,
                            "message": message
                        }
                    )
                    print(f"sent {message}")
                except Exception as exc:
                    logger.error(exc)

    async def publish(self, channel: str, message: str):
        """Send a message to the queue."""
        await self._client.publish(channel, message)

    async def consume(self):
        """Polling the queue for messages."""
        print("started to consume")
        pubsub = self._client.pubsub()
        await pubsub.subscribe("channel")
        while True:
            await asyncio.sleep(0.01)
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None and isinstance(message, dict):
                msg = json.loads(message.get("data"))
                if msg["type"] in (WSAction.PERSONAL.value,):
                    await self.send_personal_message(msg["event_id"], msg["client_id"], msg["message"])
                if msg["type"] in (WSAction.GROUP.value,):
                    await self.send_group_message(msg["event_id"], msg["message"])


room_manager = RoomManager()
