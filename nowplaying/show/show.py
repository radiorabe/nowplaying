import datetime
import logging
import logging.handlers
import uuid

from nowplaypadgen.show import Show as PadGenShow, ShowError as PadGenShowError

logger = logging.getLogger(__name__)


class ShowError(PadGenShowError):
    """Show related exception."""


class Show(PadGenShow):
    """Show object which has a start and end time and an optional URL."""

    class Options:
        def __init__(self, default_show_url: str = None):
            if not default_show_url:
                # TODO v3 remove this fallback
                logger.warning(
                    "No default show URL specified, using deprecated hardcoded default."
                )
                default_show_url = "https://www.rabe.ch/"
            self.default_show_url = default_show_url

    def __init__(self, options: Options = None):
        """Initialize a new Show object."""
        if isinstance(options, str) or options is None:
            # TODO v3 remove this fallback
            options = Show.Options()
        self.options = options
        super().__init__()

        self.name = ""
        self.url = self.options.default_show_url
        self.uuid = str(uuid.uuid4())  #: The show's global unique identifier

    def set_name(self, name):
        """Set the show's name."""
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
        return "Show '%s' (%s), start: '%s', end: '%s', url: %s" % (
            self.name,
            self.uuid,
            self.starttime,
            self.endtime,
            self.url,
        )
