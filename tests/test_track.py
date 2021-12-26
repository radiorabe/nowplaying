"""Test for :class:`Track`."""

from datetime import datetime, timedelta

import pytest
import pytz

from nowplaying.show.show import Show
from nowplaying.track.track import DEFAULT_ARTIST, DEFAULT_TITLE, Track, TrackError


def test_init():
    """Test :class:`Track`'s :meth:`.__init__` method."""
    track = Track()
    assert track.starttime == track.endtime


def test_artist():
    """Test :class:`Track`'s :meth:`artist` property."""
    track = Track()
    assert track.artist is None
    assert not track.has_default_artist()
    track.set_artist("Test")
    assert track.artist == "Test"
    assert not track.has_default_artist()
    track.set_artist(DEFAULT_ARTIST)
    assert track.has_default_artist()


def test_title():
    """Test :class:`Track`'s :meth:`title` property."""
    track = Track()
    assert track.title is None
    assert not track.has_default_title()
    track.set_title("Test Title")
    assert track.title == "Test Title"
    assert not track.has_default_title()
    track.set_title(DEFAULT_TITLE)
    assert track.has_default_title()


def test_album():
    """Test :class:`Track`'s :meth:`album` property."""
    track = Track()
    assert track.album is None
    track.set_album("Test Album")
    assert track.album == "Test Album"


def test_track():
    """Test :class:`Track`'s :meth:`track` property."""
    track = Track()
    assert track.track == 1
    track.set_track(2)
    assert track.track == 2
    with pytest.raises(TypeError):
        track.set_track("no strings allowed")
    with pytest.raises(TrackError):
        track.set_track(-1)


def test_starttime():
    """Test :class:`Track`'s :meth:`starttime` property."""
    track = Track()
    time = datetime.now(pytz.timezone("UTC"))
    original_time = track.starttime
    track.set_starttime(time)
    assert track.starttime == time
    assert track.starttime != original_time
    with pytest.raises(TrackError):
        track.set_starttime("2019-01-01")


def test_endtime():
    """Test :class:`Track`'s :meth:`endtime` property."""
    track = Track()
    time = datetime.now(pytz.timezone("UTC"))
    original_time = track.endtime
    track.set_endtime(time)
    assert track.endtime == time
    assert track.endtime != original_time
    with pytest.raises(TrackError):
        track.set_endtime("2019-01-01")


def test_show():
    """Test :class:`Track`'s :meth:`show` property."""
    track = Track()
    show = Show()
    track.set_show(show)
    assert track.show == show


def test_duration():
    """Test :class:`Track`'s :meth:`duration` property."""
    track = Track()
    assert track.get_duration() == timedelta(0)
    track.set_duration(60)
    assert track.get_duration() == timedelta(-1, 86340)


def test_prettyprinting():
    """Test :class:`Track`'s :meth:`__str__` method."""
    track = Track()
    assert "Track 'None'" in str(track)
