import logging
import urllib

from nowplaying.track.observers.base import TrackObserver

logger = logging.getLogger(__name__)


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
