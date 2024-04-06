"""Nowplaying Daemon."""

import logging
import os
import signal
import sys
import time
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Any, Self

from .api import ApiServer
from .input import observer as input_observers
from .input.handler import InputHandler
from .misc.saemubox import SaemuBox
from .options import Options
from .track.handler import TrackEventHandler
from .track.observers.dab_audio_companion import DabAudioCompanionTrackObserver
from .track.observers.icecast import IcecastTrackObserver
from .track.observers.smc_ftp import SmcFtpTrackObserver
from .track.observers.ticker import TickerTrackObserver

if TYPE_CHECKING:  # pragma: no cover
    from cloudevents.http.event import CloudEvent

_EXCEPTION_NOWPLAYING_MAIN = "Error in main"

logger = logging.getLogger(__name__)


class NowPlayingDaemon:
    """The daemon of nowplaying runs at all time and coordinates the i/o."""

    """initialize last_input to a know value."""
    last_input = 1

    def __init__(self: Self, options: Options) -> None:
        """Create NowPlayingDaemon."""
        self.options = options

        self.event_queue: Queue = Queue()
        self.saemubox = SaemuBox(
            self.options.saemubox_ip,
            self.options.check_saemubox_sender,
        )

    def main(self: Self) -> None:  # pragma: no cover
        """Run Daemon."""
        # TODO(hairmare): test once there is not saemubox in the loop
        # https://github.com/radiorabe/nowplaying/issues/179
        logger.info("Starting up now-playing daemon")
        self.saemubox.run()

        try:
            self.register_signal_handlers()

            input_handler = self.get_input_handler()
        except Exception:
            logger.exception(_EXCEPTION_NOWPLAYING_MAIN)
            sys.exit(-1)

        _thread = Thread(target=self._main_loop, args=(input_handler,))
        _thread.daemon = True
        _thread.start()

        self._start_apiserver()  # blocking

    def _start_apiserver(self: Self) -> None:
        """Start the API server."""
        self._api = ApiServer(self.options, self.event_queue)
        self._api.run_server()  # blocking

    def _stop_apiserver(self: Self) -> None:
        """Stop the API server."""
        logger.info("Stopping API server")
        self._api.stop_server()

    def _main_loop(self: Self, input_handler: InputHandler) -> None:  # pragma: no cover
        """Run main loop of the daemon.

        Should be run in a thread.
        """
        logger.info("Starting main loop")
        while True:
            try:
                saemubox_id = self.poll_saemubox()

                while not self.event_queue.empty():
                    logger.debug("Queue size: %i", self.event_queue.qsize())
                    event: CloudEvent = self.event_queue.get()
                    logger.info(
                        "Handling update from event: %s, source: %s",
                        event["type"],
                        event["source"],
                    )
                    input_handler.update(saemubox_id, event)

                input_handler.update(saemubox_id)
            except Exception:
                logger.exception(_EXCEPTION_NOWPLAYING_MAIN)

            time.sleep(self.options.sleep_seconds)

    def register_signal_handlers(self: Self) -> None:
        """Register signal handler."""
        logger.debug("Registering signal handler")
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self: Self, signum: int, *_: Any) -> None:  # noqa: ANN401
        """Handle signals."""
        logger.debug("Signal %i caught", signum)

        if signum in [signal.SIGINT, signal.SIGKILL]:
            logger.info("Signal %i caught, terminating.", signum)
            self._stop_apiserver()
            sys.exit(os.EX_OK)

    def get_track_handler(self: Self) -> TrackEventHandler:  # pragma: no cover
        """Get TrackEventHandler."""
        # TODO(hairmare): test once options have been refactored with v3
        # https://github.com/radiorabe/nowplaying/issues/179
        handler = TrackEventHandler()
        for url in self.options.icecast:
            handler.register_observer(
                IcecastTrackObserver(
                    # TODO(hairmare): v3 remove uername and password
                    #                 because we mandate specifying via url
                    # https://github.com/radiorabe/nowplaying/issues/179
                    options=IcecastTrackObserver.Options(
                        url=url,
                        username="source",
                        password=self.options.icecast_password,
                    ),
                ),
            )
        for url in self.options.dab:
            handler.register_observer(
                DabAudioCompanionTrackObserver(
                    options=DabAudioCompanionTrackObserver.Options(
                        url=url,
                        dl_plus=self.options.dab_send_dls,
                    ),
                ),
            )
        handler.register_observer(
            TickerTrackObserver(
                options=TickerTrackObserver.Options(
                    file_path=self.options.ticker_output_file,
                ),
            ),
        )
        if self.options.dab_smc:
            handler.register_observer(
                SmcFtpTrackObserver(
                    options=SmcFtpTrackObserver.Options(
                        hostname=self.options.dab_smc_ftp_hostname,
                        username=self.options.dab_smc_ftp_username,
                        password=self.options.dab_smc_ftp_password,
                    ),
                ),
            )

        return handler

    def get_input_handler(self: Self) -> InputHandler:  # pragma: no cover
        """Get InputHandler."""
        # TODO(hairmare): test once options have been refactored with v3
        # https://github.com/radiorabe/nowplaying/issues/179
        handler = InputHandler()
        track_handler = self.get_track_handler()

        klangbecken = input_observers.KlangbeckenInputObserver(
            self.options.current_show_url,
            self.options.input_file,
        )
        klangbecken.add_track_handler(track_handler)
        handler.register_observer(klangbecken)

        nonklangbecken = input_observers.NonKlangbeckenInputObserver(
            self.options.current_show_url,
        )
        nonklangbecken.add_track_handler(track_handler)
        handler.register_observer(nonklangbecken)

        return handler

    def poll_saemubox(self: Self) -> int:  # pragma: no cover
        """Poll Saemubox for new data.

        Should be run once per main loop.

        TODO(hairmare) v3 remove once replaced with pathfinder
        https://github.com/radiorabe/nowplaying/issues/179
        """
        saemubox_id = self.saemubox.get_active_output_id()
        logger.debug("Sämubox id: %i", saemubox_id)

        if self.last_input != saemubox_id:
            logger.info(
                'Sämubox changed from "%s" to "%s"',
                self.saemubox.get_id_as_name(self.last_input),
                self.saemubox.get_id_as_name(saemubox_id),
            )

        self.last_input = saemubox_id
        return saemubox_id
