import datetime
import logging
import uuid
import warnings

import isodate
import lxml.builder
import lxml.etree
import pytz

from .base import TrackObserver

logger = logging.getLogger(__name__)


class TickerTrackObserver(TrackObserver):
    """Writes the new ticker feed file.

    The feed file will be consumed by the song-ticker on the RaBe website. This is the
    successor of the long gone PseudoRssTrackObserver format used by the pre-WordPress
    website. This version here gets consumed by the WordPress website.
    """

    name = "Ticker"

    def __init__(self, ticker_file_path):
        warnings.warn(
            "The XML ticker format will be replaced with a JSON variant in the future",
            PendingDeprecationWarning,
        )
        self.ticker_file_path = ticker_file_path

    def track_started(self, track):
        logger.info(
            f"Updating Ticker XML file for track: {track.artist} - {track.title}"
        )
        try:
            tz = pytz.timezone("Europe/Zurich")
        except pytz.exceptions.UnknownTimeZoneError:  # pragma: no coverage due to not knowing how to trigger
            tz = pytz.timezone("UTC")

        now = isodate.datetime_isoformat(datetime.datetime.now(tz))

        MAIN_NAMESPACE = "http://rabe.ch/schema/ticker.xsd"
        XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
        XLINK = "{%s}" % XLINK_NAMESPACE

        E = lxml.builder.ElementMaker(
            namespace=MAIN_NAMESPACE,
            nsmap={None: MAIN_NAMESPACE, "xlink": XLINK_NAMESPACE},
        )
        show_ref = E.link(track.show.url)
        show_ref.attrib[XLINK + "type"] = "simple"
        show_ref.attrib[XLINK + "href"] = track.show.url
        show_ref.attrib[XLINK + "show"] = "replace"

        ticker = E.ticker(
            E.identifier("ticker-%s" % uuid.uuid4()),
            E.creator("now-playing daemon v2"),
            E.date(now),
            E.show(
                E.name(track.show.name),
                show_ref,
                E.startTime(
                    isodate.datetime_isoformat(track.show.starttime.astimezone(tz))
                ),
                E.endTime(
                    isodate.datetime_isoformat(track.show.endtime.astimezone(tz))
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

    def track_finished(self, track):
        return True
