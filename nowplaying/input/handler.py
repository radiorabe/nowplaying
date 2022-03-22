import logging
import logging.handlers

from cloudevents.http.event import CloudEvent

from .observer import InputObserver

logger = logging.getLogger(__name__)


class InputHandler:
    """Inform all registered input-event observers about an input status.

    This is the subject of the classical observer pattern.
    """

    def __init__(self):
        self._observers: list[InputObserver] = []

    def register_observer(self, observer: InputObserver):
        logger.info("Registering InputObserver '%s'" % observer.__class__.__name__)
        self._observers.append(observer)

    def remove_observer(self, observer: InputObserver):
        self._observers.remove(observer)

    def update(self, saemubox_id: int, event: CloudEvent = None):
        for observer in self._observers:
            logger.debug("Sending update event to observer %s" % observer.__class__)

            try:
                observer.update(saemubox_id, event)
            except Exception as e:  # pragma: no cover
                # TODO test once replaced with non generic exception
                logger.error(f"InputObserver ({observer.__class__}): {e}")
                logger.exception(e)
