from nowplaying.track import observer


class TestTrackObserver:
    def test_init(self):
        o = observer.TrackObserver()
        assert o.get_name() == "TrackObserver"
