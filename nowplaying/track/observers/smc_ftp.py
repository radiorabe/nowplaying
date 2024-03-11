"""Upload PAD to SMC."""

from __future__ import annotations

import logging
from datetime import timedelta
from ftplib import FTP_TLS
from io import BytesIO
from typing import TYPE_CHECKING, Self

from nowplaying.track.observers.base import TrackObserver

if TYPE_CHECKING:  # pragma: no cover
    import configargparse  # type: ignore[import-untyped]

    from nowplaying.track.observers.base import TTrackObserverOptions
    from nowplaying.track.track import Track


logger = logging.getLogger(__name__)

_NOWPLAYING_DAB_MAXLEN = 128


class SmcFtpTrackObserver(TrackObserver):
    """Update track metadata for DLS and DL+ to the SMC FTP server."""

    name = "SMC FTP"

    class Options(TrackObserver.Options):  # pragma: no coverage
        """Options for SmcFtpTrackObserver."""

        @classmethod
        def args(
            cls: type[TTrackObserverOptions],
            args: configargparse.ArgParser,
        ) -> None:
            """Create args."""
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
                "--dab-smc-ftp-password",
                help="Password for SMC FTP server",
            )

        def __init__(self: Self, hostname: str, username: str, password: str) -> None:
            """Create SmcFtpTrackObserver.Config."""
            self.hostname: str = hostname
            self.username: str = username
            self.password: str = password

    def __init__(self: Self, options: Options) -> None:
        """Create SmcFtpTrackObserver."""
        self._options = options

    def track_started(self: Self, track: Track) -> None:
        """Track started."""
        logger.info(
            "Updating DAB+ DLS for track artist=%s title=%s",
            track.artist,
            track.title,
        )

        if track.get_duration() < timedelta(seconds=5):
            logger.info(
                "Track is less than 5 seconds, not sending to SMC artist=%s title=%s",
                track.artist,
                track.title,
            )
            return

        dls, dlplus = _dls_from_track(track)

        # check for too long meta and shorten to just artist
        if dls.getbuffer().nbytes > _NOWPLAYING_DAB_MAXLEN:  # pragma: no cover
            logger.warning("SMC DLS to long %s", dls.getvalue().decode("latin1"))
            dls, dlplus = _dls_from_track(track, title=False)

        ftp = FTP_TLS()  # noqa: S321
        ftp.connect(self._options.hostname)
        ftp.sendcmd(f"USER {self._options.username}")
        ftp.sendcmd(f"PASS {self._options.password}")

        ftp.storlines("STOR /dls/nowplaying.dls", dls)
        ftp.storlines("STOR /dlplus/nowplaying.dls", dlplus)

        ftp.quit()
        ftp.close()

        logger.info(
            "SMC FTP hostname=%s dls=%s dlsplus=%",
            self._options.hostname,
            dls.getvalue().decode("latin1"),
            dlplus.getvalue().decode("latin1"),
        )

    def track_finished(self: Self, _: Track) -> None:
        """Track finished."""
        return


def _dls_from_track(track: Track, *, title: bool = True) -> tuple[BytesIO, BytesIO]:
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
