"""Tests for :class:`observer.TickerTrackObserver`."""

import os

import pytest

from nowplaying.track import observer

_FORMAT_WARNING = "The XML ticker format will be replaced"


@pytest.mark.filterwarnings(
    f"ignore:{_FORMAT_WARNING}:PendingDeprecationWarning:nowplaying.track.observer"
)
def test_init():
    """Test class:`observer.TickerTrackObserver`'s :meth:`.__init__` method."""
    ticker_track_observer = observer.TickerTrackObserver(ticker_file_path="")
    assert ticker_track_observer.ticker_file_path == ""


@pytest.mark.filterwarnings(
    f"ignore:{_FORMAT_WARNING}:PendingDeprecationWarning:nowplaying.track.observer"
)
def test_track_started(track_factory, show_factory):
    """Test :class:`observer.TickerTrackObserver`'s :meth:`track_started` method."""

    track = track_factory()
    track.show = show_factory()

    ticker_track_observer = observer.TickerTrackObserver(
        ticker_file_path="/tmp/track_started.xml"
    )
    ticker_track_observer.track_started(track)

    assert os.path.exists("/tmp/track_started.xml")


@pytest.mark.filterwarnings(
    f"ignore:{_FORMAT_WARNING}:PendingDeprecationWarning:nowplaying.track.observer"
)
def test_track_finished(track_factory):
    """Test :class:`observer.TickerTrackObserver`'s :meth:`track_finished` method."""
    track = track_factory()

    ticker_track_observer = observer.TickerTrackObserver(
        ticker_file_path="/tmp/dummy.xml"
    )
    assert ticker_track_observer.track_finished(track)
