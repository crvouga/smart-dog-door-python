from datetime import datetime
import math
from typing import Optional
from src.smart_door.core.model import (
    ConnectionState,
    DoorState,
    Model,
    ModelConnecting,
    ModelReady,
)


def to_door_status(model: Optional[Model], now: datetime) -> str:
    door_status = _to_door_status(model=model, now=now)
    return f"Door Status: {door_status}"


def _to_door_status(model: Optional[Model], now: datetime) -> str:
    if model is None:
        return "Unknown"
    if isinstance(model, ModelReady):
        return _to_door_status_ready(model=model, now=now)
    if isinstance(model, ModelConnecting):
        return _to_door_status_connecting(model=model, now=now)
    return "Unknown"


def _to_door_status_connecting(model: ModelConnecting, now: datetime) -> str:
    if model.door == ConnectionState.Connected:
        return f"Connected"

    return "Connecting"


def _to_door_status_ready(model: ModelReady, now: datetime) -> str:
    if model.door.state == DoorState.WillClose:
        seconds_remaining = (
            model.door.state_start_time + model.config.minimal_duration_will_close - now
        ).total_seconds()

        seconds_remaining = math.ceil(seconds_remaining)
        return f"Will close in {seconds_remaining} seconds"

    if model.door.state == DoorState.WillOpen:
        seconds_remaining = (
            model.door.state_start_time + model.config.minimal_duration_will_open - now
        ).total_seconds()

        seconds_remaining = math.ceil(seconds_remaining)
        return f"Will open in {seconds_remaining} seconds"

    if model.door.state == DoorState.Opened:
        return f"Opened"

    if model.door.state == DoorState.Closed:
        return f"Closed"

    return "Unknown"
