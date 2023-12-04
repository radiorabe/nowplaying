"""Tests for :class:`SmcFtpTrackObserver`."""
from unittest.mock import ANY, Mock, call, patch

from nowplaying.track.observers.smc_ftp import SmcFtpTrackObserver
from nowplaying.track.track import Track


def test_init():
    """Test class:`SmcFrpTrackObserver`'s :meth:`.__init__` method."""
    SmcFtpTrackObserver(
        options=SmcFtpTrackObserver.Options(
            hostname="hostname",
            username="username",
            password="password",
        )
    )


@patch("nowplaying.track.observers.smc_ftp.FTP_TLS")
def test_track_started(mock_ftp, track_factory, show_factory):
    """Test :class:`SmcFtpTrackObserver`'s :meth:`track_started` method."""
    mock_ftp_instance = Mock()
    mock_ftp.return_value = mock_ftp_instance

    track = track_factory()
    track.show = show_factory()

    smc_ftp_track_observer = SmcFtpTrackObserver(
        options=SmcFtpTrackObserver.Options(
            hostname="hostname",
            username="username",
            password="password",
        )
    )
    smc_ftp_track_observer._ftp_cls = mock_ftp
    smc_ftp_track_observer.track_started(track)
    mock_ftp.assert_called_once()
    mock_ftp_instance.assert_has_calls(
        calls=[
            call.connect("hostname"),
            call.sendcmd("USER username"),
            call.sendcmd("PASS password"),
            call.storlines(
                "STOR /dls/nowplaying.dls",
                ANY,
            ),
            call.storlines(
                "STOR /dlplus/nowplaying.dls",
                ANY,
            ),
            call.close(),
        ]
    )

    # test skipping short tracks
    track = track_factory(artist="Radio Bern", title="Livestream", duration=3)
    mock_ftp.reset_mock()
    mock_ftp_instance.reset_mock()
    smc_ftp_track_observer.track_started(track)
    mock_ftp_instance.storlines.assert_not_called()

    # test default track
    track = track_factory(artist="Radio Bern", title="Livestream", duration=60)
    track.show = show_factory()
    mock_ftp.reset_mock()
    mock_ftp_instance.reset_mock()
    smc_ftp_track_observer.track_started(track)
    mock_ftp_instance.assert_has_calls(
        calls=[
            call.connect("hostname"),
            call.sendcmd("USER username"),
            call.sendcmd("PASS password"),
            call.storlines(
                "STOR /dls/nowplaying.dls",
                ANY,
            ),
            call.storlines("STOR /dlplus/nowplaying.dls", ANY),
            call.close(),
        ]
    )


def test_track_finished():
    """Test class:`SmcFtpTrackObserver`'s :meth:`.track_finished` method."""
    smc_ftp_track_observer = SmcFtpTrackObserver(
        options=SmcFtpTrackObserver.Options(
            hostname="hostname",
            username="username",
            password="password",
        )
    )
    assert smc_ftp_track_observer.track_finished(Track())
