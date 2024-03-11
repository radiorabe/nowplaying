"""Track event handling subject of the observer."""

from __future__ import annotations

import logging
import logging.handlers
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:  # pragma: no cover
    from .observers.base import TrackObserver
    from .track import Track


logger = logging.getLogger(__name__)

_EXCEPTION_TRACK_HANDLER_ERROR_START = "Observer failed to start track"
_EXCEPTION_TRACK_HANDLER_ERROR_FINISH = "Observer failed to finish track"


class TrackEventHandler:
    """Inform all registered track-event observers about a track change.

    This is the subject of the classical observer pattern
    """

    def __init__(self: Self) -> None:
        """Initialize the track event handler."""
        self.__observers: list[TrackObserver] = []

    def register_observer(self: Self, observer: TrackObserver) -> None:
        """Register an observer to be informed about track changes."""
        logger.info("Registering TrackObserver '%s'", observer.__class__.__name__)
        self.__observers.append(observer)

    def remove_observer(self: Self, observer: TrackObserver) -> None:
        """Remove an observer from the list of observers."""
        self.__observers.remove(observer)

    def get_observers(self: Self) -> list:
        """Return register observers to allow inspecting them."""
        return self.__observers

    def track_started(self: Self, track: Track) -> None:
        """Inform all registered track-event observers about a track started event."""
        logger.info(
            "Sending track-started event to %s observers: %s",
            len(self.__observers),
            track,
        )

        for observer in self.__observers:
            logger.debug(
                "Sending track-started event to observer %s",
                observer.__class__,
            )

            try:
                observer.track_started(track)
            except Exception:
                logger.exception(_EXCEPTION_TRACK_HANDLER_ERROR_START)

    def track_finished(self: Self, track: Track) -> None:
        """Inform all registered track-event observers about a track finished event."""
        logger.info(
            "Sending track-finished event to %s observers: %s",
            len(self.__observers),
            track,
        )

        for observer in self.__observers:
            logger.debug(
                "Sending track-finished event to observer %s",
                observer.__class__,
            )

            try:
                observer.track_finished(track)
            except Exception:
                logger.exception(_EXCEPTION_TRACK_HANDLER_ERROR_FINISH)
