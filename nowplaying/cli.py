#! /usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision$"
# $Id$

import logging
import logging.handlers
import os
import signal
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import input
import input.handler
import input.observer
import track.handler
import track.observer

SAEMUBOX_STATUS_CMD = "/usr/local/scripts/songticker/get-saemubox-status.sh"
SAEMUBOX_KLANGBECKEN_ID = "1"

INPUT_FILE = "/home/endlosplayer/Eingang/now-playing.xml"

RSS_OUTPUT_FILE = "/var/www/localhost/htdocs/songticker/0.9.1/songticker.rss"

TICKER_OUTPUT_FILE = "/var/www/localhost/htdocs/songticker/0.9.3/current.xml"

# CURRENT_SHOW_URL = 'http://intranet.rabe.ch/loopy/myedit/get_current_cast.php'
# show.php is a quick and dirty libretime info grabber that generates an xml that
# resembles what loopy used to do.
CURRENT_SHOW_URL = "http://intranet.rabe.ch/pub/show.php"

# ICECAST_BASE_URL_1 = "http://10.1.1.87:8000/admin/metadata.xsl?mount=/livestream/rabe-low.mp3"
# ICECAST_BASE_URL_2 = "http://10.1.1.87:8000/admin/metadata.xsl?mount=/livestream/rabe-mid.mp3"
# ICECAST_BASE_URL_3 = "http://10.1.1.87:8000/admin/metadata.xsl?mount=/livestream/rabe-high.mp3"
# ICECAST_BASE_URL_4 = "http://10.1.1.87:8000/admin/metadata.xsl?mount=/livestream/rabe-hd.mp3"
ICECAST_BASE_URL_5 = "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-hd.mp3"
ICECAST_BASE_URL_6 = "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-high.mp3"
ICECAST_BASE_URL_7 = "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-mid.mp3"
ICECAST_BASE_URL_8 = "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-low.mp3"
ICECAST_BASE_URL_9 = "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-ultra-low.mp3"
ICECAST_BASE_URL_10 = "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-high.opus"
ICECAST_BASE_URL_11 = "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-low.opus"

DAB_AUDIO_COMPANION_BASE_URL_1 = "http://dab-04.audio.int.rabe.ch:8080"

SLEEP_SECONDS = 1


class NowPlaying:
    def __init__(self):
        pass

    def main(self):
        self.setup_logging()
        logger.info("Starting up now-playing daemon")

        try:
            self.register_signal_handlers()

            input_handler = self.get_input_handler()
        except Exception as e:
            logger.exception("Error: %s", e)
            sys.exit(-1)

        while True:
            try:
                input_handler.update()
            except Exception as e:
                logger.exception("Error: %s", e)

            time.sleep(SLEEP_SECONDS)

    def register_signal_handlers(self):
        logger.debug("Registering signal handler")
        signal.signal(signal.SIGINT, self.signal_handler)
        # signal.signal(signal.SIGKIL, self.signal_handler)

    def signal_handler(self, signum, frame):
        logger.debug("Signal %i caught" % signum)

        if signum == signal.SIGINT or signum == signal.SIGKILL:
            logger.info("Signal %i caught, terminating." % signum)
            sys.exit(os.EX_OK)

    def setup_logging(self):
        logger.setLevel(logging.DEBUG)

        syslog_handler = logging.handlers.SysLogHandler("/dev/log")

        syslog_formatter = logging.Formatter("now-playing: %(levelname)s %(message)s")

        syslog_handler.setLevel(logging.INFO)
        syslog_handler.setFormatter(syslog_formatter)

        logger.addHandler(syslog_handler)

    def get_klangbecken_track_handler(self):
        handler = track.handler.TrackEventHandler()

        # handler.register_observer(track.observer.ScrobblerTrackObserver(
        #                              SCROBBLER_USER, SCROBBLER_PWD))

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_1))

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_2))

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_3))

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_4))

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_5)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_6)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_7)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_8)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_9)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_10)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_11)
        )

        handler.register_observer(
            track.observer.TickerTrackObserver(TICKER_OUTPUT_FILE)
        )

        handler.register_observer(
            track.observer.DabAudioCompanionTrackObserver(
                DAB_AUDIO_COMPANION_BASE_URL_1
            )
        )

        return handler

    def get_nonklangbecken_track_handler(self):
        handler = track.handler.TrackEventHandler()

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_1))

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_2))

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_3))

        # handler.register_observer(track.observer.IcecastTrackObserver(
        #                              ICECAST_BASE_URL_4))

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_5)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_6)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_7)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_8)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_9)
        )

        handler.register_observer(
            track.observer.IcecastTrackObserver(ICECAST_BASE_URL_10)
        )

        handler.register_observer(
            track.observer.TickerTrackObserver(TICKER_OUTPUT_FILE)
        )

        handler.register_observer(
            track.observer.DabAudioCompanionTrackObserver(
                DAB_AUDIO_COMPANION_BASE_URL_1
            )
        )
        return handler

    def get_input_handler(self):
        klangbecken = input.observer.KlangbeckenInputObserver(
            CURRENT_SHOW_URL, INPUT_FILE
        )
        klangbecken.add_track_handler(self.get_klangbecken_track_handler())

        nonklangbecken = input.observer.NonKlangbeckenInputObserver(CURRENT_SHOW_URL)

        nonklangbecken.add_track_handler(self.get_nonklangbecken_track_handler())

        handler = input.handler.InputHandler()
        handler.register_observer(klangbecken)
        handler.register_observer(nonklangbecken)

        return handler


if __name__ == "__main__":

    # Change the default of no timeout (None) to 2 minutes, this prevents
    # endless hangs on HTTP requests.
    socket.setdefaulttimeout(120)

    http_password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    http_password_manager.add_password(
        None,
        "http://stream-master.audio.int.rabe.ch:8000/admin/",
        "source",
        os.getenv("STREAMMASTER_PASSWORD"),
    )

    urllib.request.install_opener(
        urllib.request.build_opener(
            urllib.request.HTTPBasicAuthHandler(http_password_manager)
        )
    )

    logger = logging.getLogger("now-playing")
    now_playing = NowPlaying()
    now_playing.main()
