from datetime import datetime, timedelta

import pytest
import pytz

from nowplaying.show import show
from nowplaying.track import track


class TestTrack:
    def test_default_globals(self):
        assert track.DEFAULT_ARTIST == "Radio Bern"
        assert track.DEFAULT_TITLE == "Livestream"

    def test_init(self):
        t = track.Track()
        assert t.starttime == t.endtime

    def test_artist(self):
        t = track.Track()
        assert t.artist is None
        assert not t.has_default_artist()
        t.set_artist("Test")
        assert t.artist == "Test"
        assert not t.has_default_artist()
        t.set_artist(track.DEFAULT_ARTIST)
        assert t.has_default_artist()

    def test_title(self):
        t = track.Track()
        assert t.title is None
        assert not t.has_default_title()
        t.set_title("Test Title")
        assert t.title == "Test Title"
        assert not t.has_default_title()
        t.set_title(track.DEFAULT_TITLE)
        assert t.has_default_title()

    def test_album(self):
        t = track.Track()
        assert t.album is None
        t.set_album("Test Album")
        assert t.album == "Test Album"

    def test_track(self):
        t = track.Track()
        assert t.track == 1
        t.set_track(2)
        assert t.track == 2
        with pytest.raises(TypeError):
            t.set_track("no strings allowed")
        with pytest.raises(track.TrackError):
            t.set_track(-1)

    def test_starttime(self):
        t = track.Track()
        d = datetime.now(pytz.timezone("UTC"))
        o = t.starttime
        t.set_starttime(d)
        assert t.starttime == d
        assert t.starttime != o
        with pytest.raises(track.TrackError):
            t.set_starttime("2019-01-01")

    def test_endtime(self):
        t = track.Track()
        d = datetime.now(pytz.timezone("UTC"))
        o = t.endtime
        t.set_endtime(d)
        assert t.endtime == d
        assert t.endtime != o
        with pytest.raises(track.TrackError):
            t.set_endtime("2019-01-01")

    def test_show(self):
        t = track.Track()
        s = show.Show()
        t.set_show(s)
        assert t.show == s

    def test_duration(self):
        t = track.Track()
        assert t.get_duration() == timedelta(0)
        t.set_duration(60)
        assert t.get_duration() == timedelta(-1, 86340)

    def test_prettyprinting(self):
        t = track.Track()
        assert "Track 'None'" in str(t)
