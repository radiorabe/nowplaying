from unittest.mock import MagicMock, patch

from nowplaying.track import observer, track


class TestIcecastTrackObserver:
    def test_init(self):
        o = observer.IcecastTrackObserver(baseUrl="http://localhost:80/?stream=foo.mp3")
        assert (
            o.baseUrl
            == "http://localhost:80/?stream=foo.mp3&mode=updinfo&charset=utf-8&song="
        )

    @patch("urllib.request.urlopen")
    def test_track_started(self, mock_urlopen, track_factory, show_factory):
        cm = MagicMock()
        cm.getcode.return_value = 200
        # TODO: mock and test real return value
        cm.read.return_value = "contents"
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        track = track_factory()
        track.show = show_factory()

        o = observer.IcecastTrackObserver(baseUrl="http://localhost:80/?stream=foo.mp3")
        o.track_started(track)

        mock_urlopen.assert_called_with(
            "http://localhost:80/?stream=foo.mp3&mode=updinfo&charset=utf-8&song=b%27Hairmare+and+the+Band%27+-+b%27An+Ode+to+legacy+Python+Code%27"
        )

        track = track_factory(artist="Radio Bern", title="Livestream")
        track.show = show_factory()

        o.track_started(track)
        mock_urlopen.assert_called_with(
            "http://localhost:80/?stream=foo.mp3&mode=updinfo&charset=utf-8&song=b%27Radio+Bern%27+-+b%27Hairmare+Traveling+Medicine+Show%27"
        )

    def test_track_finished(self):
        o = observer.IcecastTrackObserver(baseUrl="http://localhost:80")
        assert o.track_finished(track.Track())
