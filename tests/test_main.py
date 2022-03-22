from unittest.mock import Mock, patch

from nowplaying.__main__ import main
from nowplaying.main import NowPlaying
from nowplaying.options import Options


@patch("nowplaying.main.NowPlaying.run")
def test_entrypoint(mock_run):
    main()
    mock_run.assert_called_once()


@patch("nowplaying.main.NowPlaying._setup_otel")
@patch("nowplaying.main.NowPlaying._run_daemon")
@patch("socket.setdefaulttimeout")
def test_run(
    mock_setdefaulttimeout,
    mock_run_daemon,
    mock_setup_otel,
):
    now_playing = NowPlaying()
    now_playing.run()

    mock_setup_otel.assert_called_once()
    mock_setdefaulttimeout.assert_called_once_with(Options.socketDefaultTimeout)
    mock_run_daemon.assert_called_once()


@patch("nowplaying.main.NowPlayingDaemon")
def test_run_daemon(mock_daemon):
    options = Mock()
    mock_run = Mock()
    mock_daemon.return_value = mock_run

    now_playing = NowPlaying()
    now_playing.options = options

    now_playing._run_daemon()

    mock_daemon.assert_called_once_with(options)
    mock_run.main.assert_called_once()
