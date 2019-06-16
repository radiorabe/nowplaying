class TestTrackObserver:
    def test_get_name(self, dummy_observer):
        assert dummy_observer.get_name() == "TrackObserver"
