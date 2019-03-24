import os

from nowplaying.show import show
from nowplaying.track import observer, track


class TestTickerTrackObserver:
    def test_init(self):
        o = observer.TickerTrackObserver(ticker_file_path="")
        assert o.ticker_file_path == ""

    def test_track_started(self):
        o = observer.TickerTrackObserver(ticker_file_path="/tmp/track_started.xml")
        t = track.Track()
        t.set_artist("Hairmare and the Band")
        t.set_title("An Ode to legacy Python Code")
        t.set_album("Live at the Refactoring Club")
        t.show = show.Show()
        t.show.set_name("Hairmare Traveling Medicine Show")
        o.track_started(t)
        assert os.path.exists("/tmp/track_started.xml")
