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
            "http://localhost:80/?stream=foo.mp3&mode=updinfo&charset=utf-8&song=Hairmare+and+the+Band+-+An+Ode+to+legacy+Python+Code"
        )

        track = track_factory(artist="Radio Bern", title="Livestream")
        track.show = show_factory()

        o.track_started(track)
        mock_urlopen.assert_called_with(
            "http://localhost:80/?stream=foo.mp3&mode=updinfo&charset=utf-8&song=Radio+Bern+-+Hairmare+Traveling+Medicine+Show"
        )

    def test_track_finished(self):
        o = observer.IcecastTrackObserver(baseUrl="http://localhost:80")
        assert o.track_finished(track.Track())
