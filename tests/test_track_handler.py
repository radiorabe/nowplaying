"""Tests for :class:`TrackEventHandler`."""

from unittest.mock import Mock

from nowplaying.track.handler import TrackEventHandler


def test_init():
    """Test class:`TrackEventHandler`'s :meth:`.__init__` method."""
    track_event_handler = TrackEventHandler()

    assert len(track_event_handler.get_observers()) == 0


def test_register_observer(dummy_observer):
    """Test :class:`TrackEventHandler`'s :meth:`register_observer` method."""
    track_event_handler = TrackEventHandler()
    track_event_handler.register_observer(dummy_observer)

    assert len(track_event_handler.get_observers()) == 1


def test_remove_observer(dummy_observer):
    """Test :class:`TrackEventHandler`'s :meth:`remove_observer` method."""
    track_event_handler = TrackEventHandler()
    track_event_handler.register_observer(dummy_observer)

    assert len(track_event_handler.get_observers()) == 1

    track_event_handler.remove_observer(dummy_observer)

    assert len(track_event_handler.get_observers()) == 0


def test_track_started(track_factory):
    """Test :class:`TrackEventHandler`'s :meth:`track_started` method."""
    track = track_factory()
    mock_observer = Mock()

    track_event_handler = TrackEventHandler()
    track_event_handler.register_observer(mock_observer)

    track_event_handler.track_started(track)

    mock_observer.track_started.assert_called_with(track)


def test_track_started_isolates_exception(track_factory):
    """Test that :class:`TrackEventHandler`'s :meth:`track_started` method isolates exceptions."""
    track = track_factory()
    mock_observer = Mock()
    mock_observer.track_started.side_effect = Exception

    track_event_handler = TrackEventHandler()
    track_event_handler.register_observer(mock_observer)

    track_event_handler.track_started(track)


def test_track_finished(track_factory):
    """Test :class:`TrackEventHandler`'s :meth:`track_finished` method."""
    track = track_factory()
    mock_observer = Mock()

    track_event_handler = TrackEventHandler()
    track_event_handler.register_observer(mock_observer)

    track_event_handler.track_finished(track)

    mock_observer.track_finished.assert_called_with(track)


def test_track_finished_isolates_exception(track_factory):
    """Test that :class:`TrackEventHandler`'s :meth:`track_finished` method isolates exceptions."""
    track = track_factory()
    mock_observer = Mock()
    mock_observer.track_finished.side_effect = Exception

    track_event_handler = TrackEventHandler()
    track_event_handler.register_observer(mock_observer)

    track_event_handler.track_finished(track)
