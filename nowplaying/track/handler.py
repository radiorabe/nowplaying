import logging
import logging.handlers

from track.observer import TrackObserver

logger = logging.getLogger(__name__)


class TrackEventHandler:
    """Inform all registered track-event observers about a track change.

    This is the subject of the classical observer pattern
    """

    def __init__(self):
        self.__observers = []

    def register_observer(self, observer: TrackObserver):
        logger.info("Registering TrackObserver '%s'" % observer.__class__.__name__)
        self.__observers.append(observer)

    def remove_observer(self, observer: TrackObserver):
        self.__observers.remove(observer)

    def get_observers(self):
        """Return register observers to allow inspecting them."""
        return self.__observers

    def track_started(self, track):
        logger.info("Track started: %s" % track)

        for observer in self.__observers:
            logger.debug(
                "Sending track-started event to observer %s" % observer.__class__
            )

            try:
                observer.track_started(track)
            except Exception as e:
                # logger.error('TrackObserver (%s): %s' % observer.__class__, e)
                logger.exception(e)

    def track_finished(self, track):
        logger.info("Track finished: %s" % track)

        for observer in self.__observers:
            logger.info("Sending track-finished event")
            logger.info(
                "Sending track-finished event to observer %s" % observer.__class__
            )

            try:
                observer.track_finished(track)
            except Exception as e:
                logger.exception("TrackObserver: %s" % e)
