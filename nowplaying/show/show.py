import datetime
import logging
import logging.handlers
import uuid

import pytz

logger = logging.getLogger(__name__)

DEFAULT_SHOW_URL = "https://www.rabe.ch"


class ShowError(Exception):
    """Show related exception."""

    pass


class Show:
    """Show object which has a start and end time and an optional URL."""

    def __init__(self):
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

    def set_name(self, name):
        # The name of the show
        self.name = name

    def set_url(self, url):
        # The URL of the show
        self.url = url

    def set_starttime(self, starttime):
        if not isinstance(starttime, datetime.datetime):
            raise ShowError("starttime has to be a datatime object")

        # The show's start time as a datetime object
        self.starttime = starttime

    def set_endtime(self, endtime):
        if not isinstance(endtime, datetime.datetime):
            raise ShowError("endtime has to be a datatime object")

        # The show's end time as a datetime object
        self.endtime = endtime

    def __str__(self):
        return f"Show '{self.name}' ({self.uuid}), start: '{self.starttime}', end: '{self.endtime}', url: {self.url}"
