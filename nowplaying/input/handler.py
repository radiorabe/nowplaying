import logging
import logging.handlers

from input.observer import InputObserver

logger = logging.getLogger(__name__)


class InputHandler:
    """Inform all registered input-event observers about an input status.

    This is the subject of the classical observer pattern.
    """

    def __init__(self):
        self.__observers = []

    def register_observer(self, observer: InputObserver):
        logger.info("Registering InputObserver '%s'" % observer.__class__.__name__)
        self.__observers.append(observer)

    def remove_observer(self, observer: InputObserver):
        self.__observers.remove(observer)

    def update(self, saemubox_id: int):
        for observer in self.__observers:
            logger.debug("Sending update event to observer %s" % observer.__class__)

            try:
                observer.update(saemubox_id)
            except Exception as e:
                logger.error("InputObserver (%s): %s" % (observer.__class__, e))
                logger.exception(e)
