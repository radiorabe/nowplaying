import datetime
import logging
import logging.handlers
import uuid

import pytz

logger = logging.getLogger(__name__)

DEFAULT_ARTIST = "Radio Bern"
DEFAULT_TITLE = "Livestream"


class TrackError(Exception):
    """Track related exception."""

    pass


class Track:
    """Track object which has a start and end time and a related show."""

    def __init__(self):
        self.artist = None

        self.title = None

        self.album = None

        self.track = 1

        # The track's global unique identifier
        self.uuid = str(uuid.uuid4())

        # Get current datetime object in UTC timezone
        now = datetime.datetime.now(pytz.timezone("UTC"))

        # The show's start time, initially set to now
        self.starttime = now

        # The show's end time, initially set to to now
        self.endtime = now

    def set_artist(self, artist):
        self.artist = artist

    def set_title(self, title):
        self.title = title

    def set_album(self, album):
        self.album = album

    def set_track(self, track):
        if track < 0:
            raise TrackError("track number has to be a positive integer")

        self.track = track

    def set_starttime(self, starttime):
        if not isinstance(starttime, datetime.datetime):
            raise TrackError("starttime has to be a datatime object")

        # The track's start time as a datetime object
        self.starttime = starttime

    def set_endtime(self, endtime):
        if not isinstance(endtime, datetime.datetime):
            raise TrackError("endtime has to be a datatime object")

        # The track's end time as a datetime object
        self.endtime = endtime

    def set_duration(self, seconds):
        self.endtime = self.starttime + datetime.timedelta(seconds=int(seconds))

    def set_show(self, show):
        # if not isinstance(show, show.Show):
        #    raise TrackError('show has to be a Show object')

        # The show which the track is related to
        self.show = show

    def get_duration(self):
        return self.endtime - self.starttime

    def has_default_artist(self):
        if self.artist == DEFAULT_ARTIST:
            return True

        return False

    def has_default_title(self):
        if self.title == DEFAULT_TITLE:
            return True

        return False

    def __str__(self):
        return f"Track '{self.artist}' - '{self.title}', start: '{self.starttime}', end: '{self.endtime}', uid: {self.uuid}"
