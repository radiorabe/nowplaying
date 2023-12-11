import logging
from datetime import timedelta
from ftplib import FTP_TLS
from io import BytesIO

import configargparse

from ..track import Track
from .base import TrackObserver

logger = logging.getLogger(__name__)


class SmcFtpTrackObserver(TrackObserver):
    """Update track metadata for DLS and DL+ to the SMC FTP server."""

    name = "SMC FTP"

    class Options(TrackObserver.Options):  # pragma: no coverage
        @classmethod
        def args(cls, args: configargparse.ArgParser):
            args.add_argument(
                "--dab-smc",
                help="Enable SMC FTP delivery",
                type=bool,
                default=False,
            )
            args.add_argument(
                "--dab-smc-ftp-hostname",
                help="Hostname of SMC FTP server",
                default=[],
            )
            args.add_argument(
                "--dab-smc-ftp-username",
                help="Username for SMC FTP server",
            )
            args.add_argument(
                "--dab-smc-ftp-password", help="Password for SMC FTP server"
            )

        def __init__(self, hostname: str, username: str, password: str) -> None:
            self.hostname: str = hostname
            self.username: str = username
            self.password: str = password

    def __init__(self, options: Options):
        self._options = options

    def track_started(self, track: Track):
        logger.info(f"Updating DAB+ DLS for track: {track.artist} - {track.title}")

        if track.get_duration() < timedelta(seconds=5):
            logger.info("Track is less than 5 seconds, not sending to SMC")
            return

        dls, dlplus = _dls_from_track(track)

        # check for too long meta and shorten to just artist
        if dls.getbuffer().nbytes > 128:  # pragma: no cover
            logger.warning(f"SMC DLS to long {dls=}")
            dls, dlplus = _dls_from_track(track, title=False)

        ftp = FTP_TLS()
        ftp.connect(self._options.hostname)
        ftp.sendcmd(f"USER {self._options.username}")
        ftp.sendcmd(f"PASS {self._options.password}")

        ftp.storlines("STOR /dls/nowplaying.dls", dls)
        ftp.storlines("STOR /dlplus/nowplaying.dls", dlplus)

        ftp.quit()
        ftp.close()

        logger.info(
            f"SMC FTP Server: {self._options.hostname} DLS: {dls} DL+: {dlplus}"
        )

    def track_finished(self, track):
        return True


def _dls_from_track(track: Track, title=True) -> (BytesIO, BytesIO):
    # track.artist contains station name if no artist is set
    dls = f"{track.artist} - {track.show.name}" if title else track.artist
    dlplus = ""

    if not track.has_default_title() and not track.has_default_artist():
        dls = f"{track.artist} - {track.title}" if title else track.artist
        dlplus = (
            f"artist={track.artist}\ntitle={track.title}\n"
            if title
            else f"artist={track.artist}\n"
        )

    return (_bytes_from_string(dls), _bytes_from_string(dlplus))


def _bytes_from_string(string: str) -> BytesIO:
    b = BytesIO()
    # encode as latin1 since that is what DAB supports
    b.write(string.encode("latin1"))
    b.seek(0)
    return b
