import os

from nowplaying.show import show
from nowplaying.track import observer


class TestTickerTrackObserver:
    def test_init(self):
        o = observer.TickerTrackObserver(ticker_file_path="")
        assert o.ticker_file_path == ""

    def test_track_started(self, track_factory):
        o = observer.TickerTrackObserver(ticker_file_path="/tmp/track_started.xml")
        t = track_factory()
        t.show = show.Show()
        t.show.set_name("Hairmare Traveling Medicine Show")
        o.track_started(t)
        assert os.path.exists("/tmp/track_started.xml")
