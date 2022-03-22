# TODO scrobbling is not currently supported remove the no cover pragma from this file if you support it again
import calendar  # pragma: no cover
import logging  # pragma: no cover

import pylast  # pragma: no cover

from .base import TrackObserver  # pragma: no cover

logger = logging.getLogger(__name__)  # pragma: no cover


class ScrobblerTrackObserver(TrackObserver):  # pragma: no cover
    """Scrobble track information to last.fm and libre.fm."""

    name = "Audioscrobbler"

    lastfm_api_key = ""
    lastfm_api_secret = ""

    librefm_api_key = ""
    librefm_api_secret = ""

    def __init__(self, user, password):
        raise Exception("Unmaintained ScrobblerTrackObserver called")

        password = pylast.md5(password)

        self.lastfm = pylast.get_lastfm_network("", "", None, user, password)
        self.librefm = pylast.get_librefm_network("", "", None, user, password)

        self.scrobblers = {
            "lastfm": self.lastfm.get_scrobbler("tst", "1.0"),
            "librefm": self.librefm.get_scrobbler("tst", "1.0"),
        }

    def track_started(self, track):

        if track.has_default_artist() or track.has_default_title():
            logger.error("Default artist or title, skip now-playing scrobble")
            return False

        logger.info(
            "AS now-playing notification for track: %s - %s"
            % (track.artist, track.title)
        )

        # scrobble to all networks
        #
        # Note that track.get_duration() returns a timedelta object, which
        # could (theoretically) also contain minutes, hours and days, however
        # the track.set_duration() method only accepts seconds, therefore it's
        # safe to read track.get_duration().seconds. Python 2.7 will bring the
        # proper solution with its timedelta.total_seconds() method.
        for k, scrobbler in self.scrobblers.items():
            scrobbler.report_now_playing(
                track.artist,
                track.title,
                track.album,
                str(track.get_duration().seconds),
                str(track.track),
            )

    def track_finished(self, track):
        logger.info("Track duration was: %s" % track.get_duration().seconds)

        # if track.get_duration() < datetime.timedelta(seconds=30):
        if track.get_duration().seconds < 30:
            # respecting last.fm minimum song lenght policy of 30 seconds
            logger.info("Track duration is < 30s, skip scrobble submit")
            return False

        if track.has_default_artist() or track.has_default_title():
            logger.error("Default artist or title, skip scrobble submit")
            return False

        logger.info(f"AS submit for track: {track.artist} - {track.title}")

        # Get UTC unix timestamp without daylight saving informations
        # http://stackoverflow.com/questions/1077285/how-to-specify-time-zone-utc-when-converting-to-unix-time-python
        timestamp = calendar.timegm(track.starttime.utctimetuple())

        # scrobbling to all networks
        #
        # Note that track.get_duration() returns a timedelta object, which
        # could (theoretically) also contain minutes, hours and days, however
        # the track.set_duration() method only accepts seconds, therefore it's
        # safe to read track.get_duration().seconds. Python 2.7 will bring the
        # proper solution with its timedelta.total_seconds() method.
        for k, scrobbler in self.scrobblers.items():
            scrobbler.scrobble(
                track.artist,
                track.title,
                int(timestamp),
                "P",
                "",
                str(track.get_duration().seconds),
                track.album,
                str(track.track),
            )
