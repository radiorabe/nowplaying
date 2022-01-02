import mock

from nowplaying.daemon import NowPlayingDaemon


@mock.patch("api.ApiServer.run_server")
def test__start_apiserver(mock_run_server):
    """Test the start_apiserver function."""

    options = mock.MagicMock()
    daemon = NowPlayingDaemon(options)
    daemon._start_apiserver()

    mock_run_server.assert_called_once_with(options, daemon.event_queue)
