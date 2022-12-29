import logging
from datetime import datetime, timedelta

import configargparse
import cridlib
import requests
from radioplayer.dataclasses import (
    BroadcastType,
    Epg,
    GenreType,
    GenreTypeType,
    LongNameType,
    MediaCreditType,
    MediumNameType,
    ProgrammeType,
    RecommendationType,
    ScheduleType,
)
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from ..track import Track
from .base import TrackObserver

logger = logging.getLogger(__name__)


class RadioplayerTrackObserver(TrackObserver):
    """Update track metadata by sending PE data to radioplayer API."""

    name = "Radioplayer"

    class Options:
        @classmethod
        def args(cls, args: configargparse.ArgParser):
            args.add_argument(
                "--enable-radioplayer",
                type=bool,
                nargs="?",
                dest="radioplayer_enabled",
                help="Send ProgrammeEvent data to Radioplayer (default: False)",
                default=False,
            )
            args.add_argument(
                "--radioplayer-pi-url",
                dest="radioplayer_ingestor_url",
                help="URL to Radioplayer ingestor service, no trailing slash",
                default="https//ingest.swissradioplayer.ch/ingestor",
            )

        def __init__(
            self,
            enabled: bool,
            url: str,
            originator: str = "https://github.com/radiorabe/nowplaying",
            lang: str = "de-CH",
        ) -> None:
            self.enabled: bool = enabled
            self.url: str = url
            self.originator: str = originator
            self.lang: str = lang

    def __init__(self, options: Options):
        self._options = options
        self._xml_serializer_config = SerializerConfig(
            pretty_print=True,
            xml_declaration=False,
        )
        logger.info(
            "Radioplayer enabled: %r, url: %s"
            % (self._options.enabled, self._options.url)
        )

    def track_started(self, track: Track):
        if not self._options.enabled:
            return

        logger.info(f"Updating DAB+ DLS for track: {track.artist} - {track.title}")

        if track.get_duration() < timedelta(seconds=5):
            logger.info("Track is less than 5 seconds, not sending to Radioplayer")
            return

        if track.has_default_title() or track.has_default_artist():
            logger.info("Track is missing info, not sending data to Radioplayer")
            return

        creation_time: datetime = datetime.now()
        track_crid: str = str(cridlib.get(track.starttime))
        # The ETSI TS 102 818 V spec says:
        # The "version" attribute shall be incremented by one,
        # for every new version of the programme.
        # It's an integer so it'll last for ~8000 years if we
        # send and update once per minute.
        version: int = 1
        # this is defined by radioplay themselves
        # TODO replace with ours
        radioplayer_id: int = 1

        # generate a "simple" programme event (PE) for submitting nowplaying data to radioplayer
        epg = Epg(
            lang=self._options.lang,
            schedule=[
                ScheduleType(
                    creation_time=str(creation_time.isoformat()),
                    originator=self._options.originator,
                    version=version,
                    scope=ScheduleType.Scope(
                        start_time=track.starttime.isoformat(),
                        stop_time=track.endtime.isoformat(),
                        service_scope=[
                            ScheduleType.Scope.ServiceScope(
                                # TODO id needs to relect our SID/PI
                                id="e1.0000.0000.0",
                                radioplayer_id=radioplayer_id,
                            )
                        ],
                    ),
                    programme=[
                        ProgrammeType(
                            # TODO use programme crid here (and not track)
                            id=track_crid,
                            lang=self._options.lang,
                            # TODO should be some int, not sure what, maybe the unix ts?
                            short_id=100,
                            recommendation=RecommendationType.NO,
                            # RaBe is always "on-air" if we are able to send nowplaying PAD
                            broadcast=BroadcastType.ON_AIR,
                            # TODO what do we put here
                            # bitrate="111",
                            # version="111",
                            # TODO Show info
                            medium_name=[
                                MediumNameType(value="RaBe", lang=self._options.lang)
                            ],
                            long_name=[
                                LongNameType(
                                    value="Radio Bern RaBe", lang=self._options.lang
                                )
                            ],
                            # location=LocationType(
                            #    time=LocationType.Time(
                            #        time="2012-01-01T00:00:00+00:00", duration="PT2H"
                            #    ),
                            #    bearer=LocationType.Bearer(
                            #        id="e1.0000.0000.0", radioplayer_id="1"
                            #    ),
                            # ),
                            # TODO one we have images as described in #155
                            # media_description=MediaDescriptionType(
                            #    multimedia=MediaDescriptionType.Multimedia(
                            #        lang="en",
                            #        mime_value="image/png",
                            #        url="http://mysite.com/web-search.png",
                            #        width="86",
                            #        height="48",
                            #        index="1",
                            #    )
                            # ),
                            # Radioplayer defined this as xs:anyURI but the DAB standard has
                            # EBU TECH 3336. The best info so far on what is available is in
                            # the german radioplayer metadata companion guide:
                            # <https://www.radioplayer.de/fileadmin/fm-dam/radioplayer.de/download/RPDE_MetadataCompanionGuide_DE.pdf>
                            # TODO include specific genre once we know where to get them from
                            # TODO use general "culture" genre for now
                            genre=[
                                GenreType(
                                    type=GenreTypeType.MAIN,
                                    href="urn:radioplayer:metadata:cs:Category:2012:1",
                                    name=GenreType.Name(
                                        "Pop/Chart", lang=self._options.lang
                                    ),
                                )
                            ],
                            programme_event=[
                                ProgrammeType.ProgrammeEvent(
                                    id=track_crid,
                                    lang=self._options.lang,
                                    # TODO is required, what to put here? has to be an int
                                    short_id=0,
                                    recommendation=RecommendationType.NO,
                                    # RaBe is always "on-air" if we are able to send nowplaying PAD
                                    broadcast=BroadcastType.ON_AIR,
                                    medium_name=[
                                        MediumNameType(
                                            value=track.title, lang=self._options.lang
                                        )
                                    ],
                                    long_name=[
                                        LongNameType(
                                            value=track.title, lang=self._options.lang
                                        )
                                    ],
                                    #    location=LocationType(
                                    #        relative_time=LocationType.RelativeTime(
                                    #            time="PT1H51M23S", duration="PT3M23S"
                                    #        )
                                    #    ),
                                    # This is from the examples but should be urn:radioplayer:* if we implement it
                                    #    genre=GenreType(
                                    #        href="urn:tva:metadata:cs:ContentCS:2002:3.6.1", type=None
                                    #    ),
                                    media_credit=[
                                        MediaCreditType(
                                            role="artist",
                                            scheme="urn:ebu",
                                            value=track.artist,
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        url = f"{self._options.url}/ingestor/metadata/v1/np/"
        logger.info(f"Radioplayer: {url} data: {epg}")

        serializer = XmlSerializer(config=self._xml_serializer_config)
        xml = serializer.render(epg, ns_map={None: Epg.Meta.namespace})

        headers = {"Content-Type": "application/xml"}
        resp = requests.post(url, headers=headers, data=xml)
        if resp.status_code != 200:
            logger.error(f"Radioplayer API call failed: {resp.text} request: {xml}")

    def track_finished(self, track):
        return True
