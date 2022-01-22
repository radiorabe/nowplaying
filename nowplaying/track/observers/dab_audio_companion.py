import logging
import urllib

import requests

from .base import TrackObserver

logger = logging.getLogger(__name__)


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
