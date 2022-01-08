from mock import Mock, patch

from nowplaying.main import NowPlaying
from nowplaying.options import Options


@patch("nowplaying.main.NowPlaying.setup_logging")
@patch("nowplaying.main.NowPlaying.setup_urllib")
@patch("nowplaying.main.NowPlaying._run_daemon")
@patch("socket.setdefaulttimeout")
def test_run(
    mock_setdefaulttimeout,
    mock_run_daemon,
    mock_setup_urllib,
    mock_setup_logging,
):
    now_playing = NowPlaying()
    now_playing.run()

    mock_setup_logging.assert_called_once()
    mock_setup_urllib.assert_called_once()
    mock_setdefaulttimeout.assert_called_once_with(Options.socketDefaultTimeout)
    mock_run_daemon.assert_called_once()


@patch("urllib.request.HTTPPasswordMgrWithDefaultRealm")
@patch("urllib.request.HTTPBasicAuthHandler")
@patch("urllib.request.build_opener")
@patch("urllib.request.install_opener")
def test_setup_urllib(
    mock_install_opener,
    mock_build_opener,
    mock_basic_auth_handler,
    mock_http_password_manager,
):
    mock_http_password_manager_instance = Mock()
    mock_http_password_manager_add_password = Mock()
    mock_http_password_manager_instance.add_password = (
        mock_http_password_manager_add_password
    )
    mock_http_password_manager.return_value = mock_http_password_manager_instance

    now_playing = NowPlaying()
    options = Options()
    options.parse_known_args()
    now_playing.options = options
    now_playing.setup_urllib()

    mock_http_password_manager.assert_called_once()
    mock_http_password_manager_add_password.assert_called_once_with(
        None, "http://stream-master.audio.int.rabe.ch:8000/admin/", "source", None
    )
    mock_basic_auth_handler.assert_called_once_with(mock_http_password_manager_instance)
    mock_build_opener.assert_called_once()
    mock_install_opener.assert_called_once()
