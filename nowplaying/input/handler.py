"""Observe all input."""

from __future__ import annotations

import logging
import logging.handlers
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:  # pragma: no cover
    from cloudevents.http.event import CloudEvent

    from nowplaying.input.observer import InputObserver

logger = logging.getLogger(__name__)

_EXCEPTION_INPUT_UPDATE_FAIL = "Failed to update observer."


class InputHandler:
    """Inform all registered input-event observers about an input status.

    This is the subject of the classical observer pattern.
    """

    def __init__(self: Self) -> None:
        """Create InputHandler."""
        self._observers: list[InputObserver] = []

    def register_observer(self: Self, observer: InputObserver) -> None:
        """Register an observer."""
        logger.info("Registering InputObserver '%s'", observer.__class__.__name__)
        self._observers.append(observer)

    def remove_observer(self: Self, observer: InputObserver) -> None:
        """Remove an observer."""
        self._observers.remove(observer)

    def update(self: Self, saemubox_id: int, event: CloudEvent | None = None) -> None:
        """Update all observers."""
        for observer in self._observers:
            logger.debug("Sending update event to observer %s", observer.__class__)

            try:
                observer.update(saemubox_id, event)
            except Exception:  # pragma: no cover
                # TODO(hairmare): test once replaced with non generic exception
                # https://github.com/radiorabe/nowplaying/issues/180
                logger.exception(_EXCEPTION_INPUT_UPDATE_FAIL)
