import logging
from typing import Optional

import configargparse
import requests

from ...util import parse_icecast_url
from ..track import Track
from .base import TrackObserver

logger = logging.getLogger(__name__)


class IcecastTrackObserver(TrackObserver):
    """Update track metadata on an icecast mountpoint."""

    name = "Icecast"

    class Options(TrackObserver.Options):
        """IcecastTrackObserver options."""

        @classmethod
        def args(cls, args: configargparse.ArgParser) -> None:
            # TODO v3 remove this option
            args.add_argument(
                "-m",
                "--icecast-base",
                dest="icecastBase",
                help="Icecast base URL",
                default="http://icecast.example.org:8000/admin/",
            )
            # TODO v3 remove this option
            args.add_argument(
                "--icecast-password", dest="icecastPassword", help="Icecast Password"
            )
            args.add_argument(
                "-i",
                "--icecast",
                action="append",
                help="""Icecast endpoints, allowed multiple times. nowplaying will send metadata updates to each
                of the configured endpoints. Specify complete connection data like username and password in the
                URLs e.g. 'http://source:changeme@icecast.example.org:8000/admin/metadata.xsl?mount=/radio'.""",
                default=[],
            )

        def __init__(
            self,
            url: str,
            username: Optional[str] = None,
            password: Optional[str] = None,
            mount: Optional[str] = None,
        ):
            # TODO v3 remove optional args and only support parsed URLs
            (self.url, self.username, self.password, self.mount) = parse_icecast_url(
                url
            )
            # TODO v3 remove non URL usage of username, password, ...
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
                raise ValueError("Missing required parameter password for %s" % url)
            if not self.mount:
                raise ValueError("Missing required parameter mount for %s" % url)

    def __init__(self, options: Options):
        self.options = options
        logger.info(f"Icecast URL: {self.options.url} mount: {self.options.mount}")

    def track_started(self, track: Track):
        logger.info(
            f"Updating Icecast Metadata for track: {track.artist} - {track.title}"
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
                auth=(self.options.username, self.options.password),
                params=params,
            )
        except requests.exceptions.RequestException as e:
            logger.exception(e)

        logger.info(
            f"Icecast Metadata updated on {self.options.url} with data: {params}"
        )

    def track_finished(self, track):
        return True
