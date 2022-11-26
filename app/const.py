"""Constant."""
from enum import Enum


class WSAction(str, Enum):

    ROOM_JOIN = "ROOM_JOIN"
    BROADCAST = "BROADCAST"
    GROUP = "GROUP"
    PERSONAL = "PERSONAL"
