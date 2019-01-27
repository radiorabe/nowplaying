from datetime import datetime

import pytest
import pytz

from nowplaying.show import show


class TestShow:
    def test_init(self):
        s = show.Show()
        assert s.starttime == s.endtime

    def test_name(self):
        s = show.Show()
        assert s.name is None
        s.set_name("Test")
        assert s.name == "Test"

    def test_url(self):
        s = show.Show()
        assert s.url == show.DEFAULT_SHOW_URL
        s.set_url("http://example.com/show")
        assert s.url == "http://example.com/show"

    def test_rabe_default_url(self):
        assert show.DEFAULT_SHOW_URL == "https://www.rabe.ch"

    def test_starttime(self):
        s = show.Show()
        t = datetime.now(pytz.timezone("UTC"))
        o = s.starttime
        s.set_starttime(t)
        assert s.starttime == t
        assert s.starttime != o
        with pytest.raises(show.ShowError):
            s.set_starttime("2019-01-01")

    def test_endtime(self):
        s = show.Show()
        t = datetime.now(pytz.timezone("UTC"))
        o = s.endtime
        s.set_endtime(t)
        assert s.endtime == t
        assert s.endtime != o
        with pytest.raises(show.ShowError):
            s.set_endtime("2019-01-01")

    def test_prettyprinting(self):
        s = show.Show()
        assert "Show 'None'" in str(s)
