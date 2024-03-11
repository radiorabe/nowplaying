"""Tests for :class:`observer.TickerTrackObserver`."""

from pathlib import Path

import pytest

from nowplaying.track.observers.ticker import TickerTrackObserver

_FORMAT_WARNING = "The XML ticker format will be replaced"


@pytest.mark.filterwarnings(
    f"ignore:{_FORMAT_WARNING}:PendingDeprecationWarning:nowplaying.track.observer",
)
def test_init():
    """Test class:`TickerTrackObserver`'s :meth:`.__init__` method."""
    ticker_track_observer = TickerTrackObserver(
        options=TickerTrackObserver.Options(file_path=""),
    )
    assert ticker_track_observer.ticker_file_path == ""


@pytest.mark.filterwarnings(
    f"ignore:{_FORMAT_WARNING}:PendingDeprecationWarning:nowplaying.track.observer",
)
def test_track_started(track_factory, show_factory):
    """Test :class:`TickerTrackObserver`'s :meth:`track_started` method."""

    track = track_factory()
    track.show = show_factory()

    ticker_track_observer = TickerTrackObserver(
        options=TickerTrackObserver.Options(file_path="/tmp/track_started.xml"),
    )
    ticker_track_observer.track_started(track)

    assert Path("/tmp/track_started.xml").exists()


@pytest.mark.filterwarnings(
    f"ignore:{_FORMAT_WARNING}:PendingDeprecationWarning:nowplaying.track.observer",
)
def test_track_finished(track_factory):
    """Test :class:`TickerTrackObserver`'s :meth:`track_finished` method."""
    track = track_factory()

    ticker_track_observer = TickerTrackObserver(
        options=TickerTrackObserver.Options(file_path="/tmp/dummy.xml"),
    )
    ticker_track_observer.track_finished(track)
