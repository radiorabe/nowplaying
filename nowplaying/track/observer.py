import calendar
import datetime
import logging
import logging.handlers
import urllib.error
import urllib.parse
import urllib.request
import uuid
import warnings
from abc import ABC, abstractmethod

import isodate
import lxml.builder
import lxml.etree
import pylast
import pytz
import requests

logger = logging.getLogger(__name__)


class TrackObserver(ABC):
    """Abstract base class for all TrackObservers."""

    name = "TrackObserver"

    def get_name(self):
        return self.name

    @abstractmethod
    def track_started(self, track):  # pragma: no cover
        pass

    @abstractmethod
    def track_finished(self, track):  # pragma: no cover
        pass


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

        logger.info("AS submit for track: %s - %s" % (track.artist, track.title))

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


class IcecastTrackObserver(TrackObserver):
    """Update track metadata on an icecast mountpoint."""

    name = "Icecast"

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl + "&mode=updinfo&charset=utf-8&song="

    def track_started(self, track):
        logger.info(
            "Updating Icecast Metadata for track: %s - %s" % (track.artist, track.title)
        )

        title = track.title

        if track.has_default_title() and track.has_default_artist():
            logger.info(
                "%s: Track has default info, using show instead" % self.__class__
            )

            title = track.show.name

        song_string = urllib.parse.quote_plus("%s - %s" % (track.artist, title))

        update_url = self.baseUrl + song_string

        logger.info(f"Icecast Update URL: {update_url}")

        urllib.request.urlopen(update_url)

    def track_finished(self, track):
        return True


class TickerTrackObserver(TrackObserver):
    """Writes the new ticker feed file.

    The feed file will be consumed by the song-ticker on the RaBe website. This is the
    successor of the long gone PseudoRssTrackObserver format used by the pre-WordPress
    website. This version here gets consumed by the WordPress website.
    """

    name = "Ticker"

    def __init__(self, ticker_file_path):
        warnings.warn(
            "The XML ticker format will be replaced with a JSON variant in the future",
            PendingDeprecationWarning,
        )
        self.ticker_file_path = ticker_file_path

    def track_started(self, track):
        logger.info(
            "Updating Ticker XML file for track: %s - %s" % (track.artist, track.title)
        )
        try:
            tz = pytz.timezone("Europe/Zurich")
        except pytz.exceptions.UnknownTimeZoneError:  # pragma: no coverage due to not knowing how to trigger
            tz = pytz.timezone("UTC")

        now = isodate.datetime_isoformat(datetime.datetime.now(tz))

        MAIN_NAMESPACE = "http://rabe.ch/schema/ticker.xsd"
        XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
        XLINK = "{%s}" % XLINK_NAMESPACE

        E = lxml.builder.ElementMaker(
            namespace=MAIN_NAMESPACE,
            nsmap={None: MAIN_NAMESPACE, "xlink": XLINK_NAMESPACE},
        )
        show_ref = E.link(track.show.url)
        show_ref.attrib[XLINK + "type"] = "simple"
        show_ref.attrib[XLINK + "href"] = track.show.url
        show_ref.attrib[XLINK + "show"] = "replace"

        ticker = E.ticker(
            E.identifier("ticker-%s" % uuid.uuid4()),
            E.creator("now-playing daemon v2"),
            E.date(now),
            E.show(
                E.name(track.show.name),
                show_ref,
                E.startTime(
                    isodate.datetime_isoformat(track.show.starttime.astimezone(tz))
                ),
                E.endTime(
                    isodate.datetime_isoformat(track.show.endtime.astimezone(tz))
                ),
                id=track.show.uuid,
            ),
            E.track(
                E.show(track.show.name, ref=track.show.uuid),
                E.artist(track.artist),
                E.title(track.title),
                E.startTime(isodate.datetime_isoformat(track.starttime.astimezone(tz))),
                E.endTime(isodate.datetime_isoformat(track.endtime.astimezone(tz))),
                id=track.uuid,
            ),
        )
        lxml.etree.ElementTree(ticker).write(
            self.ticker_file_path,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )

    def track_finished(self, track):
        return True


class DabAudioCompanionTrackObserver(TrackObserver):
    """Update track metadata in a DAB+ tranmission through the 'Audio Companion' API."""

    name = "DAB+ Audio Companion"

    def __init__(self, baseUrl, dls_enabled: bool = False):
        self.baseUrl = baseUrl + "/api/setDLS"
        self.dls_enabled = self.last_frame_was_dl_plus = dls_enabled
        logger.info(
            "DAB+ Audio Companion initialised with URL: %s, DLS+ enabled: %r"
            % (
                self.baseUrl,
                self.dls_enabled,
            )
        )

    def track_started(self, track):
        logger.info(
            "Updating DAB+ DLS for track: %s - %s" % (track.artist, track.title)
        )
        # TODO v3 remove _track_started_plain
        if not self.dls_enabled:
            return self._track_started_plain(track)

        params = {}

        if not track.has_default_title() and not track.has_default_artist():
            params["artist"] = track.artist
            params["title"] = track.title
            self.last_frame_was_dl_plus = True
        elif self.last_frame_was_dl_plus:
            logger.info(
                "%s: Track has default info, using show instead. Sending DLS+ delete tags."
                % self.__class__
            )
            # track.artist contains station name if no artist is set
            message = "%s - %s" % (track.artist, track.show.name)
            param = "".join(
                (
                    "##### parameters { #####\n",
                    "DL_PLUS=1\n",
                    # delete messages for artist and title as set by Audio Companion
                    f'DL_PLUS_TAG=1 {message.find(" ")} 0\n',
                    f'DL_PLUS_TAG=4 {message.find(" ")} 0\n',
                    "##### parameters } #####\n",
                    message,
                )
            )
            params["dls"] = param
            self.last_frame_was_dl_plus = False
        else:
            logger.info(
                "%s: Track has default info, using show instead" % self.__class__
            )
            # track.artist contains station name if no artist is set
            params["dls"] = "%s - %s" % (track.artist, track.show.name)

        logger.info(f"DAB+ Audio Companion URL: {self.baseUrl} data: {params}")

        resp = requests.post(self.baseUrl, params)
        if resp.status_code != 200:
            logger.error(f"DAB+ Audio Companion API call failed: {resp.text}")

    def _track_started_plain(self, track):
        # TODO v3 remove once we always send DLS with v3
        title = track.title

        if track.has_default_title() and track.has_default_artist():
            logger.info(
                "%s: Track has default info, using show instead" % self.__class__
            )

            title = track.show.name

        # artist is an unicode string which we have to encode into UTF-8
        # http://bugs.python.org/issue216716
        song_string = urllib.parse.quote_plus(
            "%s - %s" % (track.artist.encode("utf8"), title.encode("utf8"))
        )

        update_url = f"{self.baseUrl}?dls={song_string}"

        logger.info("DAB+ Audio Companion URL: " + update_url)

        urllib.request.urlopen(update_url)

    def track_finished(self, track):
        return True
