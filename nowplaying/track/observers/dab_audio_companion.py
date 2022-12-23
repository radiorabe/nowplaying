import logging
import urllib
from datetime import timedelta

import configargparse
import requests
from nowplaypadgen.dlplus import DLPlusMessage, DLPlusObject
from nowplaypadgen.renderer.odr import ODRPadEncRenderer

from ..track import Track
from .base import TrackObserver

logger = logging.getLogger(__name__)


class DabAudioCompanionTrackObserver(TrackObserver):
    """Update track metadata in a DAB+ tranmission through the 'Audio Companion' API."""

    name = "DAB+ Audio Companion"

    class Options(TrackObserver.Options):  # pragma: no coverage
        @classmethod
        def args(cls, args: configargparse.ArgParser):
            args.add_argument(
                "-d",
                "--dab",
                action="append",
                help="DAB audio companion base URL, allowed multiple times (ie. http://dab.example.org:8080)",
                default=[],
            )
            # TODO v3 remove when stable
            args.add_argument(
                "--dab-send-dls",
                type=bool,
                nargs="?",
                dest="dab_send_dls",
                help="Send artist/title to DAB companions dls endpoint (default: True)",
                default=True,
            )

        def __init__(self, url: str, dl_plus: bool = True) -> None:
            self.url: str = url
            self.dl_plus: bool = dl_plus

    def __init__(self, options: Options):
        self._options = options
        self.base_url = options.url + "/api/setDLS"
        self.dls_enabled = self.last_frame_was_dl_plus = self._options.dl_plus
        logger.info(
            "DAB+ Audio Companion initialised with URL: %s, DLS+ enabled: %r"
            % (self.base_url, self.dls_enabled)
        )

    def track_started(self, track: Track):
        logger.info(f"Updating DAB+ DLS for track: {track.artist} - {track.title}")
        # TODO v3 remove _track_started_plain
        if not self.dls_enabled:
            return self._track_started_plain(track)

        params = {}

        if track.get_duration() < timedelta(seconds=5):
            logger.info(
                "Track is less than 5 seconds, not sending to DAB+ Audio Companion"
            )
            return

        if not track.has_default_title() and not track.has_default_artist():
            params["artist"] = track.artist
            params["title"] = track.title
            self.last_frame_was_dl_plus = True
        elif self.last_frame_was_dl_plus:
            logger.info(
                "Track has default info, using show instead. Sending DLS+ delete tags."
            )
            message = DLPlusMessage()
            # track.artist contains station name if no artist is set
            message.add_dlp_object(DLPlusObject("STATIONNAME.LONG", track.artist))
            # TODO complete integration w/o f-string (PROGAMME.NOW for show name needs a carousel + deleting)
            # message.add_dlp_object(DLPlusObject("PROGRAMME.NOW", track.show.name))
            message.add_dlp_object(DLPlusObject("ITEM.TITLE", delete=True))
            message.add_dlp_object(DLPlusObject("ITEM.ARTIST", delete=True))
            message.build(f"$STATIONNAME.LONG - {track.show.name}")
            params["dls"] = str(ODRPadEncRenderer(message))
            self.last_frame_was_dl_plus = False
        else:
            logger.info("Track has default info, using show instead")
            # track.artist contains station name if no artist is set
            params["dls"] = f"{track.artist} - {track.show.name}"

        logger.info(
            f"DAB+ Audio Companion URL: {self.base_url} data: {params} is DL+: {self.last_frame_was_dl_plus}"
        )

        resp = requests.post(self.base_url, params)
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
            f"{track.artist.encode('utf8')} - {title.encode('utf8')}"
        )

        update_url = f"{self.base_url}?dls={song_string}"

        logger.info("DAB+ Audio Companion URL: " + update_url)

        urllib.request.urlopen(update_url)

    def track_finished(self, track):
        return True
