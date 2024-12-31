"""Nowplaying Track model."""

import datetime
import logging
import logging.handlers
import uuid
from typing import Self

import pytz

from nowplaying.show.show import Show

logger = logging.getLogger(__name__)

DEFAULT_ARTIST = "Radio Bern"
DEFAULT_TITLE = "Livestream"

_EXCEPTION_TRACK_ERROR_NUMBER_NOT_INT = "track number has to be a positive integer"
_EXCEPTION_TRACK_ERROR_STARTTIME_NO_DATETIME = "starttime has to be a datetime object"
_EXCEPTION_TRACK_ERROR_ENDTIME_NO_DATETIME = "endtime has to be a datetime object"


class TrackError(Exception):
    """Track related exception."""


class Track:
    """Track object which has a start and end time and a related show."""

    def __init__(self: Self) -> None:
        """Create Track object."""
        self.artist = ""

        self.title = ""

        self.album = ""

        self.track = 1

        # The track's global unique identifier
        self.uuid = str(uuid.uuid4())

        # Get current datetime object in UTC timezone
        now = datetime.datetime.now(pytz.timezone("UTC"))

        # The show's start time, initially set to now
        self.starttime = now

        # The show's end time, initially set to to now
        self.endtime = now

    def set_artist(self: Self, artist: str) -> None:
        """Set Track artist."""
        self.artist = artist

    def set_title(self: Self, title: str) -> None:
        """Set Track title."""
        self.title = title

    def set_album(self: Self, album: str) -> None:
        """Set Track album."""
        self.album = album

    def set_track(self: Self, track: int) -> None:
        """Set Track number."""
        if track < 0:
            raise TrackError(_EXCEPTION_TRACK_ERROR_NUMBER_NOT_INT)

        self.track = track

    def set_starttime(self: Self, starttime: datetime.datetime) -> None:
        """Set Track start time."""
        if not isinstance(starttime, datetime.datetime):
            raise TrackError(_EXCEPTION_TRACK_ERROR_STARTTIME_NO_DATETIME)

        # The track's start time as a datetime object
        self.starttime = starttime

    def set_endtime(self: Self, endtime: datetime.datetime) -> None:
        """Set Track end time."""
        if not isinstance(endtime, datetime.datetime):
            raise TrackError(_EXCEPTION_TRACK_ERROR_ENDTIME_NO_DATETIME)

        # The track's end time as a datetime object
        self.endtime = endtime

    def set_duration(self: Self, seconds: int) -> None:
        """Set Track duration."""
        self.endtime = self.starttime + datetime.timedelta(seconds=int(seconds))

    def set_show(self: Self, show: Show) -> None:
        """Set Show for Track."""
        self.show = show

    def get_duration(self: Self) -> datetime.timedelta:
        """Get duration of Track."""
        return self.endtime - self.starttime

    def has_default_artist(self: Self) -> bool:
        """Return True if Track has default artist."""
        return self.artist == DEFAULT_ARTIST

    def has_default_title(self: Self) -> bool:
        """Return True if Track has default title."""
        return self.title == DEFAULT_TITLE

    def __str__(self: Self) -> str:
        """Stringify Track."""
        return (
            f"Track '{self.artist}' - '{self.title}', "
            f"start: '{self.starttime}', end: '{self.endtime}', uid: {self.uuid}"
        )
