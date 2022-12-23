import logging
import logging.handlers
import os
import time
import warnings
import xml.dom.minidom
from abc import ABC, abstractmethod

import isodate
import pytz
from cloudevents.http.event import CloudEvent

from ..show import client
from ..show.show import Show
from ..track.handler import TrackEventHandler
from ..track.track import DEFAULT_ARTIST, DEFAULT_TITLE, Track

logger = logging.getLogger(__name__)


class InputObserver(ABC):
    """Abstract base for all InputObservers."""

    _SHOW_NAME_KLANGBECKEN = "Klangbecken"
    _SHOW_URL_KLANGBECKEN = "http://www.rabe.ch/sendungen/musik/klangbecken.html"

    def __init__(self, current_show_url: str):
        self.show: Show
        self.track_handler: TrackEventHandler
        self.previous_saemubox_id: int = -1
        self.first_run = True
        self.previous_show_uuid = ""

        self.current_show_url = current_show_url

        self.showclient = client.ShowClient(current_show_url)
        self.show = self.showclient.get_show_info()

    def add_track_handler(self, track_handler: TrackEventHandler):
        self.track_handler = track_handler

    def update(self, saemubox_id: int, event: CloudEvent = None):
        # TODO v3-prep refactor to use :meth:`handles` instead of :meth:`handle_id`
        if self.handle_id(saemubox_id, event):
            self.handle(event)

    @abstractmethod
    # TODO v3 remove this method
    def handle_id(
        self, saemubox_id: int, event: CloudEvent = None
    ):  # pragma: no coverage
        pass

    @abstractmethod
    # TODO v3 remove this method
    def handle(self, event: CloudEvent = None):  # pragma: no coverage
        pass

    @abstractmethod
    def handles(self, event: CloudEvent) -> bool:  # pragma: no coverage
        pass

    @abstractmethod
    def event(self, event: CloudEvent):  # pragma: no coverage
        pass


class KlangbeckenInputObserver(InputObserver):
    """Observe cases where Sämu Box says Klangbecken is running and we can consume now-playing.xml input."""

    def __init__(
        self, current_show_url: str, input_file: str = None
    ):  # pragma: no coverage
        # TODO test once input file is replaced with api
        if input_file:
            warnings.warn(
                "The now-playing.xml format from Loopy/Klangbecken will be replaced in the future",
                PendingDeprecationWarning,
            )
            self.input_file = input_file
            self.last_modify_time = os.stat(self.input_file).st_mtime

        self.track: Track
        super().__init__(current_show_url)

    def handles(self, event: CloudEvent) -> bool:
        # TODO v3-prep call :meth:`handle_id` from here (needs saemubox_id compat workaround)
        # TODO v3 remove call to :meth:`handle_id`
        # TODO make magic string configurable
        # TODO check if source is currently on-air
        if not event:  # pragma: no coverage
            # TODO remove checking for None once only events exist
            return False
        return event["source"] == "https://github/radiorabe/klangbecken"

    def event(self, event: CloudEvent):
        self._handle(event)

    def handle_id(self, saemubox_id: int, event: CloudEvent = None):
        # only handle Klangbecken output
        if saemubox_id == 1:
            return True

        # TODO v3-prep make this get called from :meth:`handles`
        return self.handles(event)

    def handle(self, event: CloudEvent = None):
        self._handle(event)

    def _handle(self, event: CloudEvent = None):
        """Handle actual RaBe CloudEevent.

        TODO v3: move into :meth:`event` once :meth:`handle` and :meth:`handle_id` have been yeeted
        TODO v3: remove all refs to input_file and it's modify time once we use event handlers
        """
        if not event:
            # @TODO: replace the stat method with inotify
            modify_time = os.stat(self.input_file).st_mtime

        # @TODO: Need to check if we have a stale file and send default
        #        track infos in this case. This might happend if loopy
        #        went out for lunch...
        #        pseudo code: now > modify_time + self.track.get_duration()

        if self.first_run or event or modify_time > self.last_modify_time:
            logger.info("Now playing file changed")

            self.show = self.showclient.get_show_info()
            if not event:
                self.last_modify_time = modify_time

            if event:
                self.track = self.parse_event(event)
                self.first_run = False

            logger.info("First run: %s" % self.first_run)

            if not self.first_run:  # pragma: no coverage
                # TODO test once i don't have to care about mtime/inotify because it's an api
                logger.info("calling track_finished")
                self.track_handler.track_finished(self.track)

            if not event:
                # TODO remove once legacy xml is gone
                self.track = self.get_track_info()

            # Klangbecken acts as a failover and last resort input, if other
            # active inputs are silent or have problems.
            # Therefore the show's name should always be Klangbecken, regardless
            # of what loopy thinks.
            if self.show.name != self._SHOW_NAME_KLANGBECKEN:
                logger.info(
                    "Klangbecken Input active, overriding current show '%s' with '%s'"
                    % (self.show.name, self._SHOW_NAME_KLANGBECKEN)
                )

                self.show = Show()
                self.show.set_name(self._SHOW_NAME_KLANGBECKEN)
                self.show.set_url(self._SHOW_URL_KLANGBECKEN)

                # Set the show's end time to the one of the track, as we have
                # no idea for how long the Klangbecken input will be active.
                # The show's start time is initially set to now.
                self.show.set_endtime(self.track.endtime)

            self.track.set_show(self.show)

            # TODO: or finished?
            self.track_handler.track_started(self.track)

            self.first_run = False

    def get_track_info(self):
        # TODO v3 remove method once legacy xml is gone
        dom = xml.dom.minidom.parse(self.input_file)

        # default track info
        track_info = {
            "artist": DEFAULT_ARTIST,
            "title": DEFAULT_TITLE,
            "album": "",
            "track": "",
            "time": "",
        }

        song = dom.getElementsByTagName("song")

        if len(song) == 0 or song[0].hasChildNodes() is False:  # pragma: no coverage
            # TODO replace with non generic exception and test
            raise Exception("No <song> tag found")

        song = song[0]

        for name in list(track_info.keys()):
            elements = song.getElementsByTagName(name)

            if len(elements) == 0:  # pragma: no coverage
                # TODO replace with non generic exception and test
                raise Exception("No <%s> tag found" % name)
            elif elements[0].hasChildNodes():
                element_data = elements[0].firstChild.data.strip()

                if element_data != "":
                    track_info[name] = element_data
                else:  # pragma: no coverage
                    logger.info("Element %s has empty value, ignoring" % name)

        if not song.hasAttribute("timestamp"):  # pragma: no coverage
            # TODO replace with non generic exception and test
            raise Exception("Song timestamp attribute is missing")

        # set the start time and append the missing UTC offset
        # @TODO: The UTC offset should be provided by the now playing XML
        #        generated by Thomas
        # ex.: 2012-05-15T09:47:07+02:00
        track_info["start_timestamp"] = song.getAttribute("timestamp") + time.strftime(
            "%z"
        )

        current_track = Track()

        current_track.set_artist(track_info["artist"])
        current_track.set_title(track_info["title"])
        current_track.set_album(track_info["album"])

        # Store as UTC datetime object
        current_track.set_starttime(
            isodate.parse_datetime(track_info["start_timestamp"]).astimezone(
                pytz.timezone("UTC")
            )
        )

        current_track.set_duration(track_info["time"])

        return current_track

    def parse_event(self, event: CloudEvent) -> Track:
        track = Track()
        logger.info("Parsing event: %s" % event)

        track.set_artist(event.data["item.artist"])
        track.set_title(event.data["item.title"])

        event_time = isodate.parse_datetime(event["time"])
        if event["type"] == "ch.rabe.api.events.track.v1.trackStarted":
            track.set_starttime(event_time)
        elif event["type"] == "ch.rabe.api.events.track.v1.trackFinished":
            # TODO consider using now() instead of event['time']
            track.set_endtime(event_time)

        if "item.length" in event.data:
            track.set_duration(event.data["item.length"])

        logger.info("Track: %s" % track)
        return track


class NonKlangbeckenInputObserver(InputObserver):
    """Observer for input that doesn't originate from klangbecken and therefore misses the track information.

    Uses the show's name instead of the actual track infos
    """

    def handles(self, event: CloudEvent) -> bool:  # pragma: no coverage
        """Do not handle events yet.

        TODO implement this method
        TODO v3-prep call :meth:`handle_id` from here (needs saemubox_id compat workaround)
        TODO v3 remove call to :meth:`handle_id`:
        """
        return False

    def event(self, event: CloudEvent):  # pragma: no coverage
        """Do not handle events yet.

        TODO implement this method
        """
        super().event(event)

    def handle_id(self, saemubox_id: int, event: CloudEvent = None):

        if saemubox_id != self.previous_saemubox_id:
            # If sämubox changes, force a show update, this acts as
            # a self-healing measurement in case the show web service provides
            # nonsense ;)
            self.show = self.showclient.get_show_info(True)

        self.previous_saemubox_id = saemubox_id

        # only handle non-Klangbecken
        if saemubox_id != 1:
            return True

        return False

    def handle(self, event: CloudEvent = None):
        self.show = self.showclient.get_show_info()

        # only handle if a new show has started
        if self.show.uuid != self.previous_show_uuid:
            logger.info("Show changed")
            self.track_handler.track_started(self.get_track_info())
            self.previous_show_uuid = self.show.uuid

    def get_track_info(self):
        current_track = Track()

        current_track.set_artist(DEFAULT_ARTIST)
        current_track.set_title(DEFAULT_TITLE)

        # Set the track's start/end time to the start/end time of the show
        current_track.set_starttime(self.show.starttime)
        current_track.set_endtime(self.show.endtime)

        current_track.set_show(self.show)

        return current_track
