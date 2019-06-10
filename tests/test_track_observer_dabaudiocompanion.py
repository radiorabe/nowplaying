from unittest.mock import MagicMock, patch

from nowplaying.show import show
from nowplaying.track import observer, track


class TestTickerTrackObserver:
    def test_init(self):
        o = observer.DabAudioCompanionTrackObserver(baseUrl="http://localhost:80")
        assert o.baseUrl == "http://localhost:80/api/setDLS?dls="

    @patch("urllib.request.urlopen")
    def test_track_started(self, mock_urlopen, track_factory):
        cm = MagicMock()
        cm.getcode.return_value = 200
        # TODO: mock and test real return value
        cm.read.return_value = "contents"
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        o = observer.DabAudioCompanionTrackObserver(baseUrl="http://localhost:80")
        track = track_factory()
        track.show = show.Show()
        track.show.set_name("Hairmare Traveling Medicine Show")

        o.track_started(track)
        mock_urlopen.assert_called_with(
            "http://localhost:80/api/setDLS?dls=b%27Hairmare+and+the+Band%27+-+b%27An+Ode+to+legacy+Python+Code%27"
        )

    def test_track_finished(self):
        o = observer.DabAudioCompanionTrackObserver(baseUrl="http://localhost:80")
        assert o.track_finished(track.Track())
