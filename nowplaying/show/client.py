"""Show client interacts with LibreTime."""

from __future__ import annotations

import datetime
import logging
import logging.handlers
import re
from html.entities import entitydefs
from re import Match
from typing import Self

import pytz
import requests

from .show import Show

logger = logging.getLogger(__name__)

_EXCEPTION_SHOWCLIENT_NO_SHOW = "Unable to get current show information"
_EXCEPTION_SHOWCLIENT_NO_NAME = "Missing show name"
_EXCEPTION_SHOWCLIENT_NO_START = "Missing show start time"
_EXCEPTION_SHOWCLIENT_NO_END = "Missing show end time"


class ShowClientError(Exception):
    """ShowClient related exception."""


class ShowClient:
    """Fetches the show info from LibreTime now-playing v2 endpoint.

    Every show has a name, a start and endtime and an optional URL.
    """

    __DEFAULT_SHOW_DURATION = 3  # 3 seconds
    __cleanup_show_name_regexp = re.compile(r"&(\w+?);")
    __show_datetime_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self: Self, current_show_url: str) -> None:
        """Create Show."""
        self.current_show_url = current_show_url

        self.show = Show()
        self.showtz = pytz.timezone(zone="UTC")

    def get_show_info(self: Self, *, force_update: bool = False) -> Show:
        """Return a Show object."""
        if force_update:
            self.update()
        else:
            self.lazy_update()

        return self.show

    def lazy_update(self: Self) -> None:
        """Only update the info if we expect that a new show has started."""
        if datetime.datetime.now(pytz.timezone("UTC")) > self.show.endtime:
            logger.info("Show expired, going to update show info")
            self.update()

        else:
            logger.debug("Show still running, won't update show info")

    def update(self: Self) -> None:
        """Update state."""
        self.show = Show()  # Create a new show object

        # Set the show's default end time to now + 30 seconds to prevent updates
        # happening every second and hammering the web service if something
        # goes wrong later.
        self.show.set_endtime(
            datetime.datetime.now(pytz.timezone("UTC"))
            + datetime.timedelta(seconds=self.__DEFAULT_SHOW_DURATION),
        )

        try:
            # try to get the current show informations from loopy's cast web
            # service
            data = requests.get(self.current_show_url, timeout=60).json()

            logger.debug("Got show info: %s", data)

        except Exception:
            logger.exception(_EXCEPTION_SHOWCLIENT_NO_SHOW)
            # ignoring missing show update
            return

        self.showtz = pytz.timezone(zone=data["station"]["timezone"])

        # pick the current show
        show_data = self.__pick_current_show(data)

        if not show_data:
            logger.warning("Failed to find a current or upcoming show, bailing out.")
            return

        # get the name of the show, aka real_name
        # ex.: Stereo Freeze
        real_name = show_data["name"]

        if len(real_name) == 0:
            # keep the default show information
            raise ShowClientError(_EXCEPTION_SHOWCLIENT_NO_NAME)

        real_name = self.__cleanup_show_name(real_name)
        self.show.set_name(real_name)

        # get the show's end time in order to time the next lookup.
        # ex.: 2012-04-28 19:00:00 (missing a tzoffset and localized!)
        end_time = show_data["ends"]

        if len(end_time) == 0:
            raise ShowClientError(_EXCEPTION_SHOWCLIENT_NO_END)

        endtime = self.showtz.localize(
            datetime.datetime.strptime(  # noqa: DTZ007
                end_time,
                self.__show_datetime_format,
            ),
        )

        # store as UTC datetime object
        self.show.set_endtime(endtime.astimezone(pytz.timezone("UTC")))

        # get the show's start time
        # ex.: 2012-04-28 18:00:00
        start_time = show_data["starts"]

        if len(start_time) == 0:
            logger.error("No start found")
            raise ShowClientError(_EXCEPTION_SHOWCLIENT_NO_START)

        starttime = self.showtz.localize(
            datetime.datetime.strptime(  # noqa: DTZ007
                start_time,
                self.__show_datetime_format,
            ),
        )

        # store as UTC datetime object
        self.show.set_starttime(starttime.astimezone(pytz.timezone("UTC")))

        # Check if the endtime is in the past
        # This prevents stale (wrong) show informations from beeing pushed to
        # the live stream and stops hammering the service every second
        if self.show.endtime < datetime.datetime.now(pytz.timezone("UTC")):
            logger.error("Show endtime %s is in the past", self.show.endtime)

            raise ShowClientError(  # noqa: TRY003
                f"Show end time ({self.show.endtime}) is in the past",  # noqa: EM102
            )

        # get the show's URL
        # ex.: http://www.rabe.ch/sendungen/entertainment/onda-libera.html
        url = show_data["url"]

        if len(url) == 0:
            logger.error("No url found")
        else:
            self.show.set_url(url)

        logger.info(
            'Show "%s" started and runs from %s till %s',
            self.show.name,
            starttime,
            endtime,
        )
        logger.debug(self.show)

    def __cleanup_show_name(self: Self, name: str) -> str:
        """Cleanup name by undoing htmlspecialchars from libretime zf1 mvc."""

        def __entityref_decode(m: Match[str]) -> str:
            try:
                return entitydefs[m.group(1)]
            except KeyError:
                return m.group(0)

        return self.__cleanup_show_name_regexp.sub(__entityref_decode, name)

    def __pick_current_show(self: Self, data: dict[str, dict]) -> dict[str, str] | None:
        """Pick the current show from the data.

        If there is no current show and the next one starts reasonably soon, pick that.
        """
        if not data["shows"]["current"]:
            # ignore if no current show is playing
            logger.info("No current show is playing, checking next show")
            if data["shows"]["next"] and data["shows"]["next"][0]:
                show = data["shows"]["next"][0]
                logger.info("Next show is %s", show["name"])
                next_start = self.showtz.localize(
                    datetime.datetime.strptime(  # noqa: DTZ007
                        show["starts"],
                        self.__show_datetime_format,
                    ),
                )
                logger.warning(
                    "%s",
                    (
                        datetime.datetime.now(pytz.timezone("UTC"))
                        + datetime.timedelta(minutes=15)
                    ),
                )
                logger.warning(next_start)
                if next_start < datetime.datetime.now(
                    pytz.timezone("UTC"),
                ) + datetime.timedelta(minutes=15):
                    logger.info("Next show starts soon enough, using it")
                    return show
            return None
        return data["shows"]["current"]
