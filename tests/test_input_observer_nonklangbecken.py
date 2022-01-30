from datetime import datetime

from mock import Mock, patch

from nowplaying.input.observer import NonKlangbeckenInputObserver


@patch("nowplaying.show.client.ShowClient.get_show_info")
def test_handle_id(mock_get_show_info):
    show_url = "http://www.rabe.ch/klangbecken/"
    observer = NonKlangbeckenInputObserver(show_url)
    mock_get_show_info.assert_called_once()
    mock_get_show_info.reset_mock()

    saemubox_id = 1
    observer.previous_saemubox_id = saemubox_id
    assert observer.handle_id(saemubox_id) is False
    mock_get_show_info.assert_not_called()

    saemubox_id = 2
    assert observer.handle_id(saemubox_id) is True
    mock_get_show_info.assert_called_once()


@patch("nowplaying.show.client.ShowClient.get_show_info")
def test_handle(mock_get_show_info):
    show_url = "http://www.rabe.ch/klangbecken/"
    mock_track_handler = Mock()

    observer = NonKlangbeckenInputObserver(show_url)
    mock_get_show_info.assert_called_once()
    mock_get_show_info.reset_mock()

    mock_show = Mock()
    mock_show.starttime = datetime(2018, 1, 1, 0, 0, 0)
    mock_show.endtime = datetime(2018, 1, 1, 1, 0, 0)
    mock_get_show_info.return_value = mock_show

    observer.add_track_handler(mock_track_handler)
    observer.handle()
    mock_get_show_info.assert_called_once()
    assert observer.show == mock_show
