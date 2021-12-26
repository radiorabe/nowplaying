"""Tests for :class:`TrackObserver`."""


def test_get_name(dummy_observer):
    """Test :class:`TrackObserver`'s :meth:`get_name` method."""
    assert dummy_observer.get_name() == "TrackObserver"
