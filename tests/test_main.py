import logging

from mock import Mock, patch

from nowplaying.__main__ import main
from nowplaying.main import NowPlaying
from nowplaying.options import Options


@patch("nowplaying.main.NowPlaying.run")
def test_entrypoint(mock_run):
    main()
    mock_run.assert_called_once()


@patch("nowplaying.main.NowPlaying.setup_logging")
@patch("nowplaying.main.NowPlaying._run_daemon")
@patch("socket.setdefaulttimeout")
def test_run(
    mock_setdefaulttimeout,
    mock_run_daemon,
    mock_setup_logging,
):
    now_playing = NowPlaying()
    now_playing.run()

    mock_setup_logging.assert_called_once()
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


@patch("logging.StreamHandler")
@patch("logging.getLogger")
def test_setup_logging(mock_get_logger, mock_stream_handler):
    options = Mock(name="options")
    options.debug = False

    mock_root_logger = Mock(name="root_logger")
    mock_get_logger.return_value = mock_root_logger

    mock_stdout_handler = Mock(name="stdout_handler")
    mock_stream_handler.return_value = mock_stdout_handler

    now_playing = NowPlaying()
    now_playing.options = options

    now_playing.setup_logging()

    mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)
    mock_stdout_handler.setLevel.assert_called_once_with(logging.INFO)
    mock_root_logger.addHandler.assert_called_once_with(mock_stdout_handler)

    mock_root_logger.setLevel.reset_mock()
    mock_stdout_handler.setLevel.reset_mock()
    mock_root_logger.addHandler.reset_mock()
    options.debug = True

    now_playing.setup_logging()

    mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)
    mock_stdout_handler.setLevel.assert_called_with(logging.DEBUG)
    mock_root_logger.addHandler.assert_called_once_with(mock_stdout_handler)
