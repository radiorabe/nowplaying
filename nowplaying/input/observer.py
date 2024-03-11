"""Nowplaying input observer."""

from __future__ import annotations

import logging
import logging.handlers
import time
import warnings
import xml.dom.minidom
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Self

import isodate  # type: ignore[import-untyped]
import pytz

from nowplaying.show import client
from nowplaying.show.show import Show
from nowplaying.track.track import DEFAULT_ARTIST, DEFAULT_TITLE, Track

if TYPE_CHECKING:  # pragma: no cover
    from cloudevents.http.event import CloudEvent

    from nowplaying.track.handler import TrackEventHandler

logger = logging.getLogger(__name__)

_EXCEPTION_INPUT_MISSING_SONG_TAG = "No <song> tag found"
_EXCEPTION_INPUT_MISSING_TIMESTAMP = "Song timestamp attribute is missing"


class InputObserver(ABC):
    """Abstract base for all InputObservers."""

    _SHOW_NAME_KLANGBECKEN = "Klangbecken"
    _SHOW_URL_KLANGBECKEN = "http://www.rabe.ch/sendungen/musik/klangbecken.html"

    def __init__(self: Self, current_show_url: str) -> None:
        """Create InputObserver."""
        self.show: Show
        self.track_handler: TrackEventHandler
        self.previous_saemubox_id: int = -1
        self.first_run = True
        self.previous_show_uuid = ""

        self.current_show_url = current_show_url

        self.showclient = client.ShowClient(current_show_url)
        self.show = self.showclient.get_show_info()

    def add_track_handler(self: Self, track_handler: TrackEventHandler) -> None:
        """Add Track handler."""
        self.track_handler = track_handler

    def update(self: Self, saemubox_id: int, event: CloudEvent | None = None) -> None:
        """Handle update."""
        # TODO(hairmare): v3-prep refactor to use :meth:`handles`
        #                 instead of :meth:`handle_id`
        # https://github.com/radiorabe/nowplaying/issues/180
        if self.handle_id(saemubox_id, event):
            self.handle(event)

    @abstractmethod
    # TODO(hairmare): v3 remove this method
    # https://github.com/radiorabe/nowplaying/issues/179
    def handle_id(
        self: Self,
        saemubox_id: int,
        event: CloudEvent | None = None,
    ) -> bool:  # pragma: no coverage
        """Handle ID."""

    @abstractmethod
    # TODO(hairmare): v3 remove this method
    # https://github.com/radiorabe/nowplaying/issues/179
    def handle(
        self: Self,
        event: CloudEvent | None = None,
    ) -> None:  # pragma: no coverage
        """Handle event."""

    @abstractmethod
    def handles(self: Self, event: CloudEvent) -> bool:  # pragma: no coverage
        """Handle event."""

    @abstractmethod
    def event(self: Self, event: CloudEvent) -> None:  # pragma: no coverage
        """Handle event."""


class KlangbeckenInputObserver(InputObserver):
    """Observe when Sämu Box says Klangbecken we have now-playing.xml input."""

    def __init__(
        self: Self,
        current_show_url: str,
        input_file: str | None = None,
    ) -> None:  # pragma: no coverage
        """Create KlangbeckenInputObserver."""
        # TODO(hairmare): test once input file is replaced with api
        # https://github.com/radiorabe/nowplaying/issues/180
        if input_file:
            warnings.warn(
                "The now-playing.xml format from Loopy/Klangbecken "
                "will be replaced in the future",
                PendingDeprecationWarning,
                stacklevel=2,
            )
            self.input_file = input_file
            self.last_modify_time = Path(self.input_file).stat().st_mtime

        self.track: Track
        super().__init__(current_show_url)

    def handles(self: Self, event: CloudEvent | None) -> bool:
        """Check if we need to handle the event."""
        # TODO(hairmare): v3-prep call :meth:`handle_id` from here
        #                 needs saemubox_id compat workaround
        # https://github.com/radiorabe/nowplaying/issues/180
        # TODO(hairmare): v3 remove call to :meth:`handle_id`
        # https://github.com/radiorabe/nowplaying/issues/179
        # TODO(hairmare): make magic string configurable
        # https://github.com/radiorabe/nowplaying/issues/179
        # TODO(hairmare): check if source is currently on-air
        # https://github.com/radiorabe/nowplaying/issues/179
        if not event:  # pragma: no coverage
            # TODO(hairmare): remove checking for None once only events exist
            # https://github.com/radiorabe/nowplaying/issues/179
            return False
        return event["source"] == "https://github/radiorabe/klangbecken"

    def event(self: Self, event: CloudEvent) -> None:
        """Handle event."""
        self._handle(event)

    def handle_id(
        self: Self,
        saemubox_id: int,
        event: CloudEvent | None = None,
    ) -> bool:
        """Handle ID."""
        # only handle Klangbecken output
        if saemubox_id == 1:
            return True

        # TODO(hairmare): v3-prep make this get called from :meth:`handles`
        # https://github.com/radiorabe/nowplaying/issues/180
        return self.handles(event)

    def handle(self: Self, event: CloudEvent | None = None) -> None:
        """Handle RaBe CloudEevent."""
        self._handle(event)

    def _handle(self: Self, event: CloudEvent | None = None) -> None:
        """Handle actual RaBe CloudEevent.

        TODO(hairmare): v3: move into :meth:`event`
                        once :meth:`handle` and :meth:`handle_id` have been yeeted
        https://github.com/radiorabe/nowplaying/issues/179
        TODO(hairmare): v3: remove all refs to input_file and it's modify time
                        once we use event handlers
        https://github.com/radiorabe/nowplaying/issues/179
        """
        if not event:
            # @TODO(hairmare): replace the stat method with inotify
            # https://github.com/radiorabe/nowplaying/issues/179
            modify_time = Path(self.input_file).stat().st_mtime

        # @TODO(hairmare): Need to check if we have a stale file and send default
        #                  track infos in this case. This might happend if loopy
        #                  went out for lunch...
        #                  pseudo code: now > modify_time + self.track.get_duration()
        # https://github.com/radiorabe/nowplaying/issues/179

        if self.first_run or event or modify_time > self.last_modify_time:
            logger.info("Now playing file changed")

            self.show = self.showclient.get_show_info()
            if not event:
                self.last_modify_time = modify_time

            if event:
                self.track = self.parse_event(event)
                self.first_run = False

            logger.info("First run: %s", self.first_run)

            if not self.first_run:  # pragma: no coverage
                # TODO(hairmare): test once we don't have to care about
                #                 mtime/inotify because it's an api
                # https://github.com/radiorabe/nowplaying/issues/179
                logger.info("calling track_finished")
                self.track_handler.track_finished(self.track)

            if not event:
                # TODO(hairmare): remove once legacy xml is gone
                # https://github.com/radiorabe/nowplaying/issues/179
                self.track = self.get_track_info()

            # Klangbecken acts as a failover and last resort input, if other
            # active inputs are silent or have problems.
            # Therefore the show's name should always be Klangbecken, regardless
            # of what loopy thinks.
            if self.show.name != self._SHOW_NAME_KLANGBECKEN:
                logger.info(
                    "Klangbecken Input active, overriding current show '%s' with '%s'",
                    self.show.name,
                    self._SHOW_NAME_KLANGBECKEN,
                )

                self.show = Show()
                self.show.set_name(self._SHOW_NAME_KLANGBECKEN)
                self.show.set_url(self._SHOW_URL_KLANGBECKEN)

                # Set the show's end time to the one of the track, as we have
                # no idea for how long the Klangbecken input will be active.
                # The show's start time is initially set to now.
                self.show.set_endtime(self.track.endtime)

            self.track.set_show(self.show)

            # TODO(hairmare): or finished?
            # https://github.com/radiorabe/nowplaying/issues/179
            self.track_handler.track_started(self.track)

            self.first_run = False

    def get_track_info(self: Self) -> Track:
        """Get Track info."""
        # TODO(hairmare): v3 remove method once legacy xml is gone
        # https://github.com/radiorabe/nowplaying/issues/179
        dom = xml.dom.minidom.parse(self.input_file)  # noqa: S318

        # default track info
        track_info = {
            "artist": DEFAULT_ARTIST,
            "title": DEFAULT_TITLE,
            "album": "",
            "track": "",
            "time": "",
        }

        songs = dom.getElementsByTagName("song")

        if len(songs) == 0 or songs[0].hasChildNodes() is False:  # pragma: no coverage
            # TODO(hairmare): replace with non generic exception and test
            # https://github.com/radiorabe/nowplaying/issues/179
            raise Exception(_EXCEPTION_INPUT_MISSING_SONG_TAG)  # noqa: TRY002

        song = songs[0]

        for name in list(track_info.keys()):
            elements = song.getElementsByTagName(name)

            if len(elements) == 0:  # pragma: no coverage
                # TODO(hairmare): replace with non generic exception and test
                # https://github.com/radiorabe/nowplaying/issues/179
                raise Exception("No <%s> tag found" % name)  # noqa: TRY002, UP031
            if elements[0].hasChildNodes():
                element_data = elements[0].firstChild.data.strip()  # type: ignore[attr-defined,union-attr]

                if element_data != "":
                    track_info[name] = element_data
                else:  # pragma: no coverage
                    logger.info("Element %s has empty value, ignoring", name)

        if not song.hasAttribute("timestamp"):  # pragma: no coverage
            # TODO(hairmare): replace with non generic exception and test
            # https://github.com/radiorabe/nowplaying/issues/179
            raise Exception(_EXCEPTION_INPUT_MISSING_TIMESTAMP)  # noqa: TRY002

        # set the start time and append the missing UTC offset
        # @TODO: The UTC offset should be provided by the now playing XML
        #        generated by Thomas
        # ex.: 2012-05-15T09:47:07+02:00
        track_info["start_timestamp"] = song.getAttribute("timestamp") + time.strftime(
            "%z",
        )

        current_track = Track()

        current_track.set_artist(track_info["artist"])
        current_track.set_title(track_info["title"])
        current_track.set_album(track_info["album"])

        # Store as UTC datetime object
        current_track.set_starttime(
            isodate.parse_datetime(track_info["start_timestamp"]).astimezone(
                pytz.timezone("UTC"),
            ),
        )

        current_track.set_duration(int(track_info["time"]))

        return current_track

    def parse_event(self: Self, event: CloudEvent) -> Track:
        """Parse event."""
        track = Track()
        logger.info("Parsing event: %s", event)

        track.set_artist(event.data["item.artist"])
        track.set_title(event.data["item.title"])

        event_time = isodate.parse_datetime(event["time"])
        if event["type"] == "ch.rabe.api.events.track.v1.trackStarted":
            track.set_starttime(event_time)
        elif event["type"] == "ch.rabe.api.events.track.v1.trackFinished":
            track.set_endtime(event_time)

        if "item.length" in event.data:
            track.set_duration(event.data["item.length"])

        logger.info("Track: %s", track)
        return track


class NonKlangbeckenInputObserver(InputObserver):
    """Observer for input not from klangbecken ie. w/o track information.

    Uses the show's name instead of the actual track infos
    """

    def handles(self: Self, _: CloudEvent) -> bool:  # pragma: no coverage
        """Do not handle events yet.

        TODO implement this method
        TODO v3-prep call :meth:`handle_id` from here
             (needs saemubox_id compat workaround)
        TODO v3 remove call to :meth:`handle_id`:
        """
        return False

    def event(self: Self, event: CloudEvent) -> None:  # pragma: no coverage
        """Do not handle events yet.

        TODO implement this method
        """

    def handle_id(self: Self, saemubox_id: int, _: CloudEvent | None = None) -> bool:
        """Handle new ID from Saemubox."""
        if saemubox_id != self.previous_saemubox_id:
            # If sämubox changes, force a show update, this acts as
            # a self-healing measurement in case the show web service provides
            # nonsense ;)
            self.show = self.showclient.get_show_info(force_update=True)

        self.previous_saemubox_id = saemubox_id

        # only handle non-Klangbecken
        return saemubox_id != 1

    def handle(self: Self, _: CloudEvent | None = None) -> None:
        """Handle Track."""
        self.show = self.showclient.get_show_info()

        # only handle if a new show has started
        if self.show.uuid != self.previous_show_uuid:
            logger.info("Show changed")
            self.track_handler.track_started(self.get_track_info())
            self.previous_show_uuid = self.show.uuid

    def get_track_info(self: Self) -> Track:
        """Get Track info."""
        current_track = Track()

        current_track.set_artist(DEFAULT_ARTIST)
        current_track.set_title(DEFAULT_TITLE)

        # Set the track's start/end time to the start/end time of the show
        current_track.set_starttime(self.show.starttime)
        current_track.set_endtime(self.show.endtime)

        current_track.set_show(self.show)

        return current_track
