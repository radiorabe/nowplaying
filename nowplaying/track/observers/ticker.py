"""TickerTrackObserver generates the songticker.xml file."""

from __future__ import annotations

import datetime
import logging
import uuid
import warnings
from typing import TYPE_CHECKING, Self

import isodate  # type: ignore[import-untyped]
import lxml.builder  # type: ignore[import-untyped]
import lxml.etree
import pytz

from nowplaying.track.observers.base import TrackObserver, TTrackObserverOptions

if TYPE_CHECKING:  # pragma: no cover
    import configargparse  # type: ignore[import-untyped]

    from nowplaying.track.track import Track

logger = logging.getLogger(__name__)


class TickerTrackObserver(TrackObserver):
    """Writes the new ticker feed file.

    The feed file will be consumed by the song-ticker on the RaBe website. This is the
    successor of the long gone PseudoRssTrackObserver format used by the pre-WordPress
    website. This version here gets consumed by the WordPress website.
    """

    name = "Ticker"

    class Options(TrackObserver.Options):
        """TickerTrackObserver options."""

        @classmethod
        def args(
            cls: type[TTrackObserverOptions],
            args: configargparse.ArgParser,
        ) -> None:
            """Build args."""
            args.add_argument(
                "--xml-output",
                dest="tickerOutputFile",
                help="ticker XML output format",
                default="/var/www/localhost/htdocs/songticker/0.9.3/current.xml",
            )

        def __init__(self: Self, file_path: str) -> None:
            """Create TickerTrackObserver.Config."""
            self.file_path = file_path

    def __init__(self: Self, options: Options) -> None:
        """Create TickerTrackObserver."""
        warnings.warn(
            "The XML ticker format will be replaced with a JSON variant in the future",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.ticker_file_path = options.file_path

    def track_started(self: Self, track: Track) -> None:
        """Track started."""
        logger.info(
            "Updating Ticker XML file for track: %s - %s",
            track.artist,
            track.title,
        )
        try:
            tz = pytz.timezone("Europe/Zurich")
        except (
            pytz.exceptions.UnknownTimeZoneError
        ):  # pragma: no coverage due to not knowing how to trigger
            tz = pytz.timezone("UTC")

        now = isodate.datetime_isoformat(datetime.datetime.now(tz))

        MAIN_NAMESPACE = "http://rabe.ch/schema/ticker.xsd"  # noqa: N806
        XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"  # noqa: N806
        XLINK = "{%s}" % XLINK_NAMESPACE  # noqa: N806, UP031

        E = lxml.builder.ElementMaker(  # noqa: N806
            namespace=MAIN_NAMESPACE,
            nsmap={None: MAIN_NAMESPACE, "xlink": XLINK_NAMESPACE},
        )
        show_ref = E.link(track.show.url)
        show_ref.attrib[XLINK + "type"] = "simple"
        show_ref.attrib[XLINK + "href"] = track.show.url
        show_ref.attrib[XLINK + "show"] = "replace"

        ticker = E.ticker(
            E.identifier(f"ticker-{uuid.uuid4()}"),
            E.creator("now-playing daemon v2"),
            E.date(now),
            E.show(
                E.name(track.show.name),
                show_ref,
                E.startTime(
                    isodate.datetime_isoformat(track.show.starttime.astimezone(tz)),
                ),
                E.endTime(
                    isodate.datetime_isoformat(track.show.endtime.astimezone(tz)),
                ),
                id=track.show.uuid,
            ),
            E.track(
                E.show(track.show.name, ref=track.show.uuid),
                E.artist(track.artist),
                E.title(track.title),
                E.startTime(isodate.datetime_isoformat(track.starttime.astimezone(tz))),
                E.endTime(isodate.datetime_isoformat(track.endtime.astimezone(tz))),
                id=track.uuid,
            ),
        )
        lxml.etree.ElementTree(ticker).write(
            self.ticker_file_path,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )

    def track_finished(self: Self, _: Track) -> None:
        """Track finished."""
