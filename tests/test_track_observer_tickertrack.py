import os

from nowplaying.track import observer


class TestTickerTrackObserver:
    def test_init(self):
        o = observer.TickerTrackObserver(ticker_file_path="")
        assert o.ticker_file_path == ""

    def test_track_started(self, track_factory, show_factory):
        t = track_factory()
        t.show = show_factory()

        o = observer.TickerTrackObserver(ticker_file_path="/tmp/track_started.xml")
        o.track_started(t)

        assert os.path.exists("/tmp/track_started.xml")

    def test_track_finished(self, track_factory):
        t = track_factory()

        o = observer.TickerTrackObserver(ticker_file_path="/tmp/dummy.xml")
        assert o.track_finished(t)
