"""Tests for :class:`Show`."""

from datetime import datetime

import pytest
import pytz
from nowplaypadgen.show import Show as PadGenShow

from nowplaying.show.show import DEFAULT_SHOW_URL, Show, ShowError


def test_init():
    """Test :class:`Show`'s :meth:`.__init__` method."""
    show = Show()
    assert isinstance(show, PadGenShow)


def test_name():
    """Test :class:`Show`'s :meth:`name` property."""
    show = Show()
    assert show.name is None
    show.set_name("Test")
    assert show.name == "Test"


def test_url():
    """Test :class:`Show`'s :meth:`url` property."""
    show = Show()
    assert show.url == DEFAULT_SHOW_URL
    show.set_url("http://example.com/show")
    assert show.url == "http://example.com/show"


def test_starttime():
    """Test :class:`Show`'s :meth:`starttime` property."""
    show = Show()
    time = datetime.now(pytz.timezone("UTC"))
    original_time = show.starttime
    show.set_starttime(time)
    assert show.starttime == time
    assert show.starttime != original_time
    with pytest.raises(ShowError):
        show.set_starttime("2019-01-01")


def test_endtime():
    """Test :class:`Show`'s :meth:`endtime` property."""
    show = Show()
    time = datetime.now(pytz.timezone("UTC"))
    original_time = show.endtime
    show.set_endtime(time)
    assert show.endtime == time
    assert show.endtime != original_time
    with pytest.raises(ShowError):
        show.set_endtime("2019-01-01")


def test_prettyprinting():
    """Test :class:`Show`'s :meth:`__str__` method."""
    show = Show()
    assert "Show 'None'" in str(show)
