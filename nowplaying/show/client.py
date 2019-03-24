#! /usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision$"
# $Id$

import datetime
import logging
import logging.handlers
import urllib.error
import urllib.parse
import urllib.request
import xml.dom.minidom

import isodate
import pytz

from . import show

logger = logging.getLogger("now-playing")

DEFAULT_SHOW_DURATION = 30  # 30 seconds


class ShowClientError(Exception):
    """ShowClient related exception."""

    pass


class ShowClient:
    """Client which fetches the show informations from the cast-web-service.

    Every show has a name, a start and endtime and an optional URL.
    """

    def __init__(self, current_show_url):

        self.current_show_url = current_show_url

        self.show = show.Show()

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
        self.show = show.Show()  # Create a new show object

        # Set the show's default end time to now + 30 seconds to prevent updates
        # happening every second and hammering the web service if something
        # goes wrong later.
        self.show.set_endtime(
            datetime.datetime.now(pytz.timezone("UTC"))
            + datetime.timedelta(seconds=DEFAULT_SHOW_DURATION)
        )

        try:
            # try to get the current show informations from loopy's cast web
            # service
            dom = xml.dom.minidom.parse(urllib.request.urlopen(self.current_show_url))

        except Exception as e:
            logger.error("%s: Unable to get current show informations" % self.__class__)

            logger.exception(e)
            # LSB 2017: ignoring missing show update
            # raise ShowClientError('Unable to get show informations: %s' % e)
            return

        # get the name of the show, aka real_name
        # ex.: Stereo Freeze
        real_name = dom.getElementsByTagName("real_name")

        if len(real_name) == 0 or real_name[0].hasChildNodes() is False:
            # keep the default show information
            logger.error("%s: No <real_name> tag found" % self.__class__)
            raise ShowClientError("Missing show name")

        self.show.set_name(real_name[0].firstChild.data.strip())

        # get the show's end time in order to time the next lookup.
        # ex.: 2012-04-28T19:00:00+0200
        end_time = dom.getElementsByTagName("end_time")

        if len(end_time) == 0 or end_time[0].hasChildNodes() is False:
            logger.error("%s: No <end_time> tag found" % self.__class__)
            raise ShowClientError("Missing show end time")

        endtime = isodate.parse_datetime(end_time[0].firstChild.data.strip())

        # store as UTC datetime object
        self.show.set_endtime(endtime.astimezone(pytz.timezone("UTC")))

        # get the show's start time
        # ex.: 2012-04-28T18:00:00+0200
        start_time = dom.getElementsByTagName("start_time")

        if len(start_time) == 0 or start_time[0].hasChildNodes() is False:
            logger.error("%s: No <start_time> tag found" % self.__class__)
            raise ShowClientError("Missing show start time")

        starttime = isodate.parse_datetime(start_time[0].firstChild.data.strip())

        # store as UTC datetime object
        self.show.set_starttime(starttime.astimezone(pytz.timezone("UTC")))

        # Check if the endtime is in the past
        # This prevents stale (wrong) show informations from beeing pushed to
        # the live stream and stops hammering the service every second
        if self.show.endtime < datetime.datetime.now(pytz.timezone("UTC")):
            logger.error(
                "%s: Show endtime %s is in the past"
                % (self.__class__, self.show.endtime)
            )

            raise ShowClientError(
                "Show end time (%s) is in the past" % self.show.endtime
            )

        # get the show's URL
        # ex.: http://www.rabe.ch/sendungen/entertainment/onda-libera.html
        url = dom.getElementsByTagName("url")

        if len(url) == 0 or start_time[0].hasChildNodes() is False:
            logger.error("%s: No <url> tag found" % self.__class__)
        else:
            self.show.set_url(url[0].firstChild.data.strip())

        logger.info(
            'Show "%s" started and runs from %s till %s'
            % (self.show.name, starttime, endtime)
        )

        logger.info(self.show)
