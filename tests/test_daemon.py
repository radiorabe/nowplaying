"""Tests for :class:`NowPlayingDaemon`."""

from os import EX_OK
from signal import SIGINT
from unittest.mock import Mock, patch

import pytest

from nowplaying.daemon import NowPlayingDaemon
from nowplaying.misc.saemubox import SaemuBox


@pytest.fixture(name="options")
def fixture_options():
    class _Options:
        def __init__(self):
            self.saemubox_ip = ""
            self.check_saemubox_sender = True

    return _Options()


@patch("signal.signal")
def test_register_signal_handlers(mock_signal_signal, options):
    """Test :meth:`register_signal_handlers` method."""
    nowplaying_daemon = NowPlayingDaemon(options)
    nowplaying_daemon.register_signal_handlers()

    mock_signal_signal.assert_called_with(SIGINT, nowplaying_daemon.signal_handler)


@patch("sys.exit")
def test_signal_handler(mock_sys_exit, options):
    """Test :meth:`signal_handler` method."""

    with patch.object(SaemuBox, "__init__", lambda *_: None):
        nowplaying_daemon = NowPlayingDaemon(options)
        nowplaying_daemon._api = Mock()  # noqa: SLF001
        nowplaying_daemon.signal_handler(SIGINT, None)

        nowplaying_daemon._api.stop_server.assert_called_once()  # noqa: SLF001
        mock_sys_exit.assert_called_with(EX_OK)


@patch("nowplaying.api.ApiServer.run_server")
def test__start_apiserver(mock_run_server, options):
    """Test the start_apiserver function."""

    with patch.object(SaemuBox, "__init__", lambda *_: None):
        daemon = NowPlayingDaemon(options)

        daemon._start_apiserver()  # noqa: SLF001

    mock_run_server.assert_called_with()
