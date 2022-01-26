"""Tests for :class:`observer.IcecastTrackObserver`."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from nowplaying.track.observers.icecast import IcecastTrackObserver
from nowplaying.track.track import Track


@pytest.mark.parametrize(
    "kwargs,url,username,password,mount",
    [
        (
            {"url": "http://user:password@localhost:80/?mount=foo.mp3"},
            "http://localhost:80/",
            "user",
            "password",
            "foo.mp3",
        ),
        (
            {"url": "http://user:password@localhost:80/", "mount": "foo.mp3"},
            "http://localhost:80/",
            "user",
            "password",
            "foo.mp3",
        ),
        (
            {"url": "http://localhost:80/?mount=foo.mp3", "password": "password"},
            "http://localhost:80/",
            "source",
            "password",
            "foo.mp3",
        ),
        (
            {"url": "http://user:password@localhost/?mount=foo.mp3"},
            "http://localhost:80/",
            "user",
            "password",
            "foo.mp3",
        ),
    ],
)
def test_options(kwargs, url, username, password, mount):
    options = IcecastTrackObserver.Options(**kwargs)

    assert options.url == url
    assert options.username == username
    assert options.password == password
    assert options.mount == mount


def test_init():
    """Test class:`IcecastTrackObserver`'s :meth:`.__init__` method."""
    icecast_track_observer = IcecastTrackObserver(
        options=IcecastTrackObserver.Options(
            url="http://localhost:80/?mount=foo.mp3",
            username="foo",
            password="bar",
        )
    )
    assert icecast_track_observer.options.url == "http://localhost:80/"
    assert icecast_track_observer.options.mount == "foo.mp3"

    icecast_track_observer = IcecastTrackObserver(
        options=IcecastTrackObserver.Options(
            url="http://localhost:80/",
            username="foo",
            password="bar",
            mount="foo.mp3",
        )
    )
    assert icecast_track_observer.options.url == "http://localhost:80/"
    assert icecast_track_observer.options.mount == "foo.mp3"

    # test for exception if mount is missing
    with pytest.raises(ValueError):
        IcecastTrackObserver.Options(
            url="http://localhost:80/",
            username="foo",
            password="bar",
        )

    # test for exception if password is missing
    with pytest.raises(ValueError):
        IcecastTrackObserver.Options(
            url="http://localhost:80/?mount=foo.mp3",
            username="foo",
        )


@patch("requests.get")
def test_track_started(mock_requests_get, track_factory, show_factory):
    """Test :class:`IcecastTrackObserver`'s :meth:`track_started` method."""
    mock_resp = MagicMock()
    mock_resp.getcode.return_value = 200
    # TODO: mock and test real return value
    mock_resp.read.return_value = "contents"
    mock_resp.__enter__.return_value = mock_resp
    mock_requests_get.return_value = mock_resp

    track = track_factory()
    track.show = show_factory()

    icecast_track_observer = IcecastTrackObserver(
        options=IcecastTrackObserver.Options(
            url="http://localhost:80/?mount=foo.mp3",
            username="foo",
            password="bar",
        )
    )
    icecast_track_observer.track_started(track)

    mock_requests_get.assert_called_with(
        "http://localhost:80/",
        auth=("foo", "bar"),
        params={
            "mount": "foo.mp3",
            "mode": "updinfo",
            "charset": "utf-8",
            "song": "Hairmare and the Band - An Ode to legacy Python Code",
        },
    )
    track = track_factory(artist="Radio Bern", title="Livestream")
    track.show = show_factory()

    icecast_track_observer.track_started(track)
    mock_requests_get.assert_called_with(
        "http://localhost:80/",
        auth=("foo", "bar"),
        params={
            "mount": "foo.mp3",
            "mode": "updinfo",
            "charset": "utf-8",
            "song": "Radio Bern - Hairmare Traveling Medicine Show",
        },
    )

    # test for ignoring of failed requests
    mock_requests_get.reset_mock()
    mock_requests_get.side_effect = requests.exceptions.RequestException
    icecast_track_observer.track_started(track)
    mock_requests_get.assert_called_with(
        "http://localhost:80/",
        auth=("foo", "bar"),
        params={
            "mount": "foo.mp3",
            "mode": "updinfo",
            "charset": "utf-8",
            "song": "Radio Bern - Hairmare Traveling Medicine Show",
        },
    )


def test_track_finished():
    """Test :class:`IcecastTrackObserver`'s :meth:`track_finished` method."""
    icecast_track_observer = IcecastTrackObserver(
        options=IcecastTrackObserver.Options(
            url="http://localhost:80/?mount=foo.mp3",
            username="foo",
            password="bar",
        )
    )
    assert icecast_track_observer.track_finished(Track())
