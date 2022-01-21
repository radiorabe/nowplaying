"""Tests for :class:`observer.IcecastTrackObserver`."""

from unittest.mock import MagicMock, patch

from nowplaying.track.observers.icecast import IcecastTrackObserver
from nowplaying.track.track import Track


def test_init():
    """Test class:`IcecastTrackObserver`'s :meth:`.__init__` method."""
    icecast_track_observer = IcecastTrackObserver(
        baseUrl="http://localhost:80/?stream=foo.mp3"
    )
    assert (
        icecast_track_observer.baseUrl
        == "http://localhost:80/?stream=foo.mp3&mode=updinfo&charset=utf-8&song="
    )


@patch("urllib.request.urlopen")
def test_track_started(mock_urlopen, track_factory, show_factory):
    """Test :class:`IcecastTrackObserver`'s :meth:`track_started` method."""
    mock_resp = MagicMock()
    mock_resp.getcode.return_value = 200
    # TODO: mock and test real return value
    mock_resp.read.return_value = "contents"
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    track = track_factory()
    track.show = show_factory()

    icecast_track_observer = IcecastTrackObserver(
        baseUrl="http://localhost:80/?stream=foo.mp3"
    )
    icecast_track_observer.track_started(track)

    base_request = (
        "http://localhost:80/?stream=foo.mp3&mode=updinfo&charset=utf-8&song="
    )

    mock_urlopen.assert_called_with(
        f"{base_request}Hairmare+and+the+Band+-+An+Ode+to+legacy+Python+Code"
    )

    track = track_factory(artist="Radio Bern", title="Livestream")
    track.show = show_factory()

    icecast_track_observer.track_started(track)
    mock_urlopen.assert_called_with(
        f"{base_request}Radio+Bern+-+Hairmare+Traveling+Medicine+Show"
    )


def test_track_finished():
    """Test :class:`IcecastTrackObserver`'s :meth:`track_finished` method."""
    icecast_track_observer = IcecastTrackObserver(baseUrl="http://localhost:80")
    assert icecast_track_observer.track_finished(Track())
