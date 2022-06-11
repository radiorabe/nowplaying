import logging
import urllib
from datetime import timedelta

import requests

from ..track import Track
from .base import TrackObserver

logger = logging.getLogger(__name__)


class DabAudioCompanionTrackObserver(TrackObserver):
    """Update track metadata in a DAB+ tranmission through the 'Audio Companion' API."""

    name = "DAB+ Audio Companion"

    def __init__(self, base_url, dls_enabled: bool = False):
        self.base_url = base_url + "/api/setDLS"
        self.dls_enabled = self.last_frame_was_dl_plus = dls_enabled
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
            # track.artist contains station name if no artist is set
            message = f"{track.artist} - {track.show.name}"
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
