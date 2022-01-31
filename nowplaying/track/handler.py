"""Track event handling subject of the observer."""

import logging
import logging.handlers

from .observers.base import TrackObserver
from .track import Track

logger = logging.getLogger(__name__)


class TrackEventHandler:
    """Inform all registered track-event observers about a track change.

    This is the subject of the classical observer pattern
    """

    def __init__(self):
        """Initialize the track event handler."""
        self.__observers = []

    def register_observer(self, observer: TrackObserver):
        """Register an observer to be informed about track changes."""
        logger.info("Registering TrackObserver '%s'", observer.__class__.__name__)
        self.__observers.append(observer)

    def remove_observer(self, observer: TrackObserver):
        """Remove an observer from the list of observers."""
        self.__observers.remove(observer)

    def get_observers(self) -> list:
        """Return register observers to allow inspecting them."""
        return self.__observers

    def track_started(self, track: Track):
        """Inform all registered track-event observers about a track started event."""
        logger.info(
            "Sending track-started event to %s observers: %s",
            len(self.__observers),
            track,
        )

        for observer in self.__observers:
            logger.debug(
                "Sending track-started event to observer %s", observer.__class__
            )

            try:
                observer.track_started(track)
            except Exception as error:
                logger.exception(error)

    def track_finished(self, track: Track):
        """Inform all registered track-event observers about a track finished event."""
        logger.info(
            "Sending track-finished event to %s observers: %s",
            len(self.__observers),
            track,
        )

        for observer in self.__observers:
            logger.debug(
                "Sending track-finished event to observer %s", observer.__class__
            )

            try:
                observer.track_finished(track)
            except Exception as error:
                logger.exception(error)
