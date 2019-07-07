from unittest.mock import Mock

from nowplaying.track import handler


class TestTrackEventHandler:
    def test_init(self):
        h = handler.TrackEventHandler()

        assert len(h.get_observers()) == 0

    def test_register_observer(self, dummy_observer):
        h = handler.TrackEventHandler()
        h.register_observer(dummy_observer)

        assert len(h.get_observers()) == 1

    def test_remove_observer(self, dummy_observer):
        h = handler.TrackEventHandler()
        h.register_observer(dummy_observer)

        assert len(h.get_observers()) == 1

        h.remove_observer(dummy_observer)

        assert len(h.get_observers()) == 0

    def test_track_started(self, track_factory):
        t = track_factory()
        mock_observer = Mock()

        h = handler.TrackEventHandler()
        h.register_observer(mock_observer)

        h.track_started(t)

        mock_observer.track_started.assert_called_with(t)

    def test_track_started_isolates_exception(self, track_factory):
        t = track_factory()
        mock_observer = Mock()
        mock_observer.track_started.side_effect = Exception

        h = handler.TrackEventHandler()
        h.register_observer(mock_observer)

        h.track_started(t)

    def test_track_finished(self, track_factory):
        t = track_factory()
        mock_observer = Mock()

        h = handler.TrackEventHandler()
        h.register_observer(mock_observer)

        h.track_finished(t)

        mock_observer.track_finished.assert_called_with(t)

    def test_track_finished_isolates_exception(self, track_factory):
        t = track_factory()
        mock_observer = Mock()
        mock_observer.track_finished.side_effect = Exception

        h = handler.TrackEventHandler()
        h.register_observer(mock_observer)

        h.track_finished(t)
