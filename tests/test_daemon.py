"""Tests for :class:`NowPlayingDaemon`."""

from os import EX_OK
from signal import SIGINT

from mock import MagicMock, patch

from nowplaying.daemon import NowPlayingDaemon
from nowplaying.misc.saemubox import SaemuBox


@patch("signal.signal")
def test_register_signal_handlers(mock_signal_signal):
    """Test :meth:`register_signal_handlers` method."""
    nowplaying_daemon = NowPlayingDaemon({})
    nowplaying_daemon.register_signal_handlers()

    mock_signal_signal.assert_called_with(SIGINT, nowplaying_daemon.signal_handler)


@patch("sys.exit")
def test_signal_handler(mock_sys_exit):
    """Test :meth:`signal_handler` method."""

    with patch.object(SaemuBox, "__init__", lambda x, y, z: None):
        nowplaying_daemon = NowPlayingDaemon({})
        nowplaying_daemon.signal_handler(SIGINT, None)

        mock_sys_exit.assert_called_with(EX_OK)


@patch("api.ApiServer.run_server")
def test__start_apiserver(mock_run_server):
    """Test the start_apiserver function."""

    options = MagicMock()
    daemon = NowPlayingDaemon(options)
    daemon._start_apiserver()

    mock_run_server.assert_called_once_with(options, daemon.event_queue)
