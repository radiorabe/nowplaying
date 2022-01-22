import datetime
import logging
import logging.handlers
import re
from html.entities import entitydefs

import pytz
import requests

from .show import Show

logger = logging.getLogger(__name__)


class ShowClientError(Exception):
    """ShowClient related exception."""

    pass


class ShowClient:
    """Client which fetches the show informations from the LibreTime now-playing v2 endpoint.

    Every show has a name, a start and endtime and an optional URL.
    """

    __DEFAULT_SHOW_DURATION = 3  # 3 seconds
    __cleanup_show_name_regexp = re.compile(r"&(\w+?);")

    def __init__(self, current_show_url):

        self.current_show_url = current_show_url

        self.show = Show()

    def get_show_info(self, force_update=False):
        """Return a Show object."""

        if force_update:
            self.update()
        else:
            self.lazy_update()

        return self.show

    def lazy_update(self):
        # only update the info if we expect that a new show has started
        if datetime.datetime.now(pytz.timezone("UTC")) > self.show.endtime:
            logger.info("Show expired, going to update show info")
            self.update()

        else:
            logger.debug("Show still running, won't update show info")

    def update(self):
        self.show = Show()  # Create a new show object

        # Set the show's default end time to now + 30 seconds to prevent updates
        # happening every second and hammering the web service if something
        # goes wrong later.
        self.show.set_endtime(
            datetime.datetime.now(pytz.timezone("UTC"))
            + datetime.timedelta(seconds=self.__DEFAULT_SHOW_DURATION)
        )

        try:
            # try to get the current show informations from loopy's cast web
            # service
            data = requests.get(self.current_show_url).json()

            logger.debug("Got show info: %s" % data)

        except Exception as e:
            logger.error("Unable to get current show informations")

            logger.exception(e)
            # LSB 2017: ignoring missing show update
            # raise ShowClientError('Unable to get show informations: %s' % e)
            return

        if not data["shows"]["current"]:
            # ignore if no current show is playing
            logger.warning("No current show is playing")
            return

        # get the name of the show, aka real_name
        # ex.: Stereo Freeze
        real_name = data["shows"]["current"]["name"]

        if len(real_name) == 0:
            # keep the default show information
            logger.error("No show name found")
            raise ShowClientError("Missing show name")

        real_name = self.__cleanup_show_name(real_name)
        self.show.set_name(real_name)

        showtz = pytz.timezone(data["station"]["timezone"])

        # get the show's end time in order to time the next lookup.
        # ex.: 2012-04-28 19:00:00 (missing a tzoffset and localized!)
        end_time = data["shows"]["current"]["ends"]

        if len(end_time) == 0:
            logger.error("No end found")
            raise ShowClientError("Missing show end time")

        endtime = showtz.localize(
            datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        )

        # store as UTC datetime object
        self.show.set_endtime(endtime.astimezone(pytz.timezone("UTC")))

        # get the show's start time
        # ex.: 2012-04-28 18:00:00
        start_time = data["shows"]["current"]["starts"]

        if len(start_time) == 0:
            logger.error("No start found")
            raise ShowClientError("Missing show start time")

        starttime = showtz.localize(
            datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        )

        # store as UTC datetime object
        self.show.set_starttime(starttime.astimezone(pytz.timezone("UTC")))

        # Check if the endtime is in the past
        # This prevents stale (wrong) show informations from beeing pushed to
        # the live stream and stops hammering the service every second
        if self.show.endtime < datetime.datetime.now(pytz.timezone("UTC")):
            logger.error("Show endtime %s is in the past" % self.show.endtime)

            raise ShowClientError(
                "Show end time (%s) is in the past" % self.show.endtime
            )

        # get the show's URL
        # ex.: http://www.rabe.ch/sendungen/entertainment/onda-libera.html
        url = data["shows"]["current"]["url"]

        if len(url) == 0:
            logger.error("No url found")
        else:
            self.show.set_url(url)

        logger.info(
            'Show "%s" started and runs from %s till %s'
            % (self.show.name, starttime, endtime)
        )
        logger.debug(self.show)

    def __cleanup_show_name(self, name) -> str:
        """Cleanup name by undoing htmlspecialchars from libretime zf1 mvc."""

        def __entityref_decode(m):
            try:
                return entitydefs[m.group(1)]
            except KeyError:
                return m.group(0)

        return self.__cleanup_show_name_regexp.sub(__entityref_decode, name)
