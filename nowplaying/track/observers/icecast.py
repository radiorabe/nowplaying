"""Send PAD to icecast endpoints."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

import requests

from nowplaying.track.observers.base import TrackObserver
from nowplaying.util import parse_icecast_url

if TYPE_CHECKING:  # pragma: no cover
    import configargparse  # type: ignore[import-untyped]

    from nowplaying.track.observers.base import TTrackObserverOptions
    from nowplaying.track.track import Track

logger = logging.getLogger(__name__)

_NOWPLAYING_TRACK_EXEPTION = "request failed"


class IcecastTrackObserver(TrackObserver):
    """Update track metadata on an icecast mountpoint."""

    name = "Icecast"

    class Options(TrackObserver.Options):
        """IcecastTrackObserver options."""

        @classmethod
        def args(
            cls: type[TTrackObserverOptions],
            args: configargparse.ArgParser,
        ) -> None:
            """Args for IcecastTrackObserver."""
            # TODO(hairmare): v3 remove this option
            # https://github.com/radiorabe/nowplaying/issues/179
            args.add_argument(
                "-m",
                "--icecast-base",
                dest="icecast_base",
                help="Icecast base URL",
                default="http://icecast.example.org:8000/admin/",
            )
            # TODO(hairmare): v3 remove this option
            # https://github.com/radiorabe/nowplaying/issues/179
            args.add_argument(
                "--icecast-password",
                dest="icecast_password",
                help="Icecast Password",
            )
            args.add_argument(
                "-i",
                "--icecast",
                action="append",
                help="""Icecast endpoints, allowed multiple times. nowplaying
                will send metadata updates to each of the configured endpoints.
                Specify complete connection data like username and password in
                the URLs e.g. 'http://source:changeme@icecast.example.org:8000/admin/metadata.xsl?mount=/radio'.""",
                default=[],
            )

        def __init__(
            self: Self,
            url: str,
            username: str | None = None,
            password: str | None = None,
            mount: str | None = None,
        ) -> None:
            """Create IcecastTrackObserver.Config."""
            # TODO(hairmare): v3 remove optional args and only support parsed URLs
            # https://github.com/radiorabe/nowplaying/issues/179
            (self.url, self.username, self.password, self.mount) = parse_icecast_url(
                url,
            )
            # TODO(hairmare): v3 remove non URL usage of username, password, ...
            # https://github.com/radiorabe/nowplaying/issues/179
            if not self.username and username:
                # grab from args if not in URL
                logger.warning("deprecated use username from URL")
                self.username = username
            if not self.username:
                # default to source if neither in URL nor args
                logger.warning("deprecated use username from URL")
                self.username = "source"
            if not self.password and password:
                # grab from args if not in URL
                logger.warning("deprecated use password from URL")
                self.password = password
            if not self.mount and mount:
                # grab from args if not in URL
                logger.warning("deprecated use mount from URL")
                self.mount = mount
            if not self.password:
                raise ValueError(f"Missing required parameter password for {url}")  # noqa: EM102, TRY003
            if not self.mount:
                raise ValueError(f"Missing required parameter mount for {url}")  # noqa: EM102, TRY003

    def __init__(self: Self, options: Options) -> None:
        """Create IcecastTrackObserver."""
        self.options = options
        logger.info("Icecast URL: %s mount: %s", self.options.url, self.options.mount)

    def track_started(self: Self, track: Track) -> None:
        """Track started."""
        logger.info(
            "Updating Icecast Metadata for track: %s - %s",
            track.artist,
            track.title,
        )

        title = track.title

        if track.has_default_title() and track.has_default_artist():
            logger.info("Track has default info, using show instead")

            title = track.show.name

        params = {
            "mount": self.options.mount,
            "mode": "updinfo",
            "charset": "utf-8",
            "song": f"{track.artist} - {title}",
        }
        try:
            requests.get(
                self.options.url,
                auth=(self.options.username, self.options.password),  # type: ignore[arg-type]
                params=params,
                timeout=60,
            )
        except requests.exceptions.RequestException:
            logger.exception(_NOWPLAYING_TRACK_EXEPTION)

        logger.info(
            "Icecast Metadata updated on %s with data: %s",
            self.options.url,
            params,
        )

    def track_finished(self: Self, _: Track) -> None:
        """Track finished."""
        return
