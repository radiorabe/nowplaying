"""Nowplaying Show model."""

import datetime
import logging
import logging.handlers
import uuid
from typing import Self

import pytz

logger = logging.getLogger(__name__)

DEFAULT_SHOW_URL = "https://www.rabe.ch"

_EXCEPTION_SHOW_ERROR_STARTTIME_NO_DATETIME = "starttime has to be a datetime object"
_EXCEPTION_SHOW_ERROR_ENDTIME_NO_DATETIME = "endtime has to be a datetime object"


class ShowError(Exception):
    """Show related exception."""


class Show:
    """Show object which has a start and end time and an optional URL."""

    def __init__(self: Self) -> None:
        """Create Show."""
        self.name = ""

        self.url = DEFAULT_SHOW_URL

        # The show's global unique identifier
        self.uuid = str(uuid.uuid4())

        # Get current datetime object in UTC timezone
        now = datetime.datetime.now(pytz.timezone("UTC"))

        # The show's start time, initially set to now
        self.starttime = now

        # The show's end time, initially set to to now
        self.endtime = now

    def set_name(self: Self, name: str) -> None:
        """Set Show name."""
        # The name of the show
        self.name = name

    def set_url(self: Self, url: str) -> None:
        """Set Show URL."""
        # The URL of the show
        self.url = url

    def set_starttime(self: Self, starttime: datetime.datetime) -> None:
        """Set Show start time."""
        if not isinstance(starttime, datetime.datetime):
            raise ShowError(_EXCEPTION_SHOW_ERROR_STARTTIME_NO_DATETIME)

        # The show's start time as a datetime object
        self.starttime = starttime

    def set_endtime(self: Self, endtime: datetime.datetime) -> None:
        """Set Show end time."""
        if not isinstance(endtime, datetime.datetime):
            raise ShowError(_EXCEPTION_SHOW_ERROR_ENDTIME_NO_DATETIME)

        # The show's end time as a datetime object
        self.endtime = endtime

    def __str__(self: Self) -> str:
        """Stringify Show."""
        return (
            f"Show '{self.name}' ({self.uuid}), "
            f"start: '{self.starttime}', end: '{self.endtime}', url: {self.url}"
        )
