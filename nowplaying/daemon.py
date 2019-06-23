import logging
import os
import signal
import sys
import time

from input import observer as inputObservers
from input.handler import InputHandler
from misc.saemubox import SaemuBox
from track import observer as trackObservers
from track.handler import TrackEventHandler

logger = logging.getLogger(__name__)


class NowPlayingDaemon:
    """The daemon part of the nowplaying app runs at all time and coordinates the input and output."""

    """initialize last_input to a know value."""
    last_input = 1

    def __init__(self, options):
        self.options = options

        self.saemubox = SaemuBox()

    def main(self):
        logger.info("Starting up now-playing daemon")

        try:
            self.register_signal_handlers()

            input_handler = self.get_input_handler()
        except Exception as e:
            logger.exception("Error: %s", e)
            sys.exit(-1)

        while True:
            try:
                saemubox_id = self.poll_saemubox()

                input_handler.update(saemubox_id)
            except Exception as e:
                logger.exception("Error: %s", e)

            time.sleep(self.options.sleepSeconds)

    def register_signal_handlers(self):
        logger.debug("Registering signal handler")
        signal.signal(signal.SIGINT, self.signal_handler)
        # signal.signal(signal.SIGKIL, self.signal_handler)

    def signal_handler(self, signum, frame):
        logger.debug("Signal %i caught" % signum)

        if signum == signal.SIGINT or signum == signal.SIGKILL:
            logger.info("Signal %i caught, terminating." % signum)
            sys.exit(os.EX_OK)

    def get_track_handler(self):
        handler = TrackEventHandler()
        [
            handler.register_observer(trackObservers.IcecastTrackObserver(url))
            for url in self.options.icecast
        ]
        [
            handler.register_observer(
                trackObservers.DabAudioCompanionTrackObserver(url)
            )
            for url in self.options.dab
        ]
        handler.register_observer(
            trackObservers.TickerTrackObserver(self.options.tickerOutputFile)
        )

        return handler

    def get_input_handler(self):
        handler = InputHandler()

        klangbecken = inputObservers.KlangbeckenInputObserver(
            self.options.currentShowUrl, self.options.inputFile
        )
        klangbecken.add_track_handler(self.get_track_handler())
        handler.register_observer(klangbecken)

        nonklangbecken = inputObservers.NonKlangbeckenInputObserver(
            self.options.currentShowUrl
        )
        nonklangbecken.add_track_handler(self.get_track_handler())
        handler.register_observer(nonklangbecken)

        return handler

    def poll_saemubox(self):
        """
        Poll Saemubox for new data.

        Should be run once per main loop.
        """

        saemubox_id = self.saemubox.get_active_output_id()
        logger.debug("Sämubox id: %i" % saemubox_id)

        if self.last_input != saemubox_id:
            logger.info(
                'Sämubox changed from "%s" to "%s"'
                % (
                    self.saemubox.get_id_as_name(self.last_input),
                    self.saemubox.get_id_as_name(saemubox_id),
                )
            )

        self.last_input = saemubox_id
        return saemubox_id
