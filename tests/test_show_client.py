"""Tests for :class:`ShowClient`."""

import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
import pytz
import requests

from nowplaying.show.client import ShowClient, ShowClientError
from nowplaying.show.show import Show

_BASE_URL = "http://example.com/api/live-info-v2/format/json"


def file_get_contents(filename: str) -> str:
    """Read a file and returns its contents."""
    with open(filename) as file:
        return file.read()


def test_init():
    """Test :class:`ShowClient`'s :meth:`.__init__` method."""
    show_client = ShowClient(_BASE_URL)
    assert show_client.current_show_url == _BASE_URL


def test_get_show_info():
    """Test :class:`ShowClient`'s :meth:`get_show_info` method."""
    show_client = ShowClient(_BASE_URL)
    show_client.lazy_update = Mock()
    show_client.update = Mock()

    show_client.get_show_info()
    show_client.lazy_update.assert_called_once()
    show_client.update.assert_not_called()


def test_get_show_info_with_force_update_true():
    """Test :class:`ShowClient`'s :meth:`get_show_info` method with force_update=True."""
    show_client = ShowClient(_BASE_URL)
    show_client.lazy_update = Mock()
    show_client.update = Mock()

    show_client.get_show_info(force_update=True)
    show_client.lazy_update.assert_not_called()
    show_client.update.assert_called_once()


def test_lazy_update():
    """Test :class:`ShowClient`'s :meth:`lazy_update` method."""
    show_client = ShowClient(_BASE_URL)
    show_client.update = Mock()
    show_client.get_show_info = Mock()

    # it calls update if the show is not set
    show_client.lazy_update()
    show_client.update.assert_called_once()


@patch("logging.Logger.debug")
def test_lazy_update_with_show_set(mock_logger_debug):
    """Test :class:`ShowClient`'s :meth:`lazy_update` method with a show set."""
    show_client = ShowClient(_BASE_URL)
    show_client.update = Mock()
    show_client.get_show_info = Mock()
    show = Show()
    show.endtime = datetime.now(pytz.timezone("UTC")) + timedelta(hours=1)
    show_client.show = show

    # it does not call update if the show is set and the show has not ended
    show_client.lazy_update()
    show_client.update.assert_not_called()
    mock_logger_debug.assert_called_once_with(
        "Show still running, won't update show info"
    )


@patch("requests.get")
def test_update(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method."""
    mock_requests_get.return_value.json = Mock(
        return_value=json.loads(
            file_get_contents("tests/fixtures/cast_now_during_show.json")
        )
    )
    show_client = ShowClient(_BASE_URL)
    show_client.update()
    assert show_client.show.name == "Voice of Hindu Kush"
    assert show_client.show.starttime == datetime(
        2019, 1, 27, 13, tzinfo=pytz.timezone("UTC")
    )
    assert show_client.show.endtime == datetime(
        2319, 1, 27, 14, tzinfo=pytz.timezone("UTC")
    )
    assert show_client.show.url == "https://www.rabe.ch/stimme-der-kutuesch/"


@patch("requests.get")
def test_update_connection_error(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method when a connection error occurs.

    It should not crash if external api refuses to connect.
    """
    mock_requests_get.side_effect = requests.exceptions.ConnectionError()
    show_client = ShowClient(_BASE_URL)
    show_client.update()
    assert show_client.show.name == ""
    assert show_client.show.url == "https://www.rabe.ch"


@patch("requests.get")
def test_update_no_url(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method when no url is returned."""
    mock_requests_get.return_value.json = Mock(
        return_value=json.loads(
            file_get_contents("tests/fixtures/cast_now_no_url.json")
        )
    )
    show_client = ShowClient(_BASE_URL)
    show_client.update()
    assert show_client.show.url == "https://www.rabe.ch"


@patch("requests.get")
@pytest.mark.parametrize(
    "fixture,field",
    [
        ("cast_now_no_name", "name"),
        ("cast_now_no_end", "end time"),
        ("cast_now_no_start", "start time"),
    ],
)
def test_update_empty_field(mock_requests_get, fixture, field):
    """Test :class:`ShowClient`'s :meth:`update` method when a field is empty."""
    mock_requests_get.return_value.json = Mock(
        return_value=json.loads(file_get_contents(f"tests/fixtures/{fixture}.json"))
    )
    show_client = ShowClient(_BASE_URL)
    with pytest.raises(ShowClientError) as info:
        show_client.update()
    assert str(info.value) == f"Missing show {field}"


@patch("requests.get")
def test_update_past_show(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method when the show is in the past."""
    mock_requests_get.return_value.json = Mock(
        return_value=json.loads(
            file_get_contents("tests/fixtures/cast_now_past_show.json")
        )
    )
    show_client = ShowClient(_BASE_URL)
    with pytest.raises(ShowClientError) as info:
        show_client.update()
    assert str(info.value) == "Show end time (2019-01-27 14:00:00+00:00) is in the past"


@patch("requests.get")
def test_update_show_empty(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method when the show is empty.

    It should not crash if external api has no info.
    """
    mock_requests_get.return_value.json = Mock(
        return_value=json.loads(
            file_get_contents("tests/fixtures/cast_now_show_empty.json")
        )
    )
    show_client = ShowClient(_BASE_URL)
    show_client.update()
    assert show_client.show.name == ""
    assert show_client.show.url == "https://www.rabe.ch"


@patch("requests.get")
def test_update_show_encoding_fix_in_name(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method when the show name has an encoding fix."""
    mock_requests_get.return_value.json = Mock(
        return_value=json.loads(
            file_get_contents("tests/fixtures/cast_now_show_encoding_fix.json")
        )
    )
    show_client = ShowClient(_BASE_URL)
    show_client.update()
    assert show_client.show.name == "Rhythm & Blues Juke Box öç &nope;"


@patch("requests.get")
def test_update_when_show_is_in_next_array(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method."""
    mock_requests_get.return_value.json = Mock(
        return_value=json.loads(
            file_get_contents("tests/fixtures/cast_now_show_in_next.json")
        )
    )
    show_client = ShowClient(_BASE_URL)
    show_client.update()
    assert show_client.show.name == "Voice of Hindu Kush"
    assert show_client.show.starttime == datetime(
        2019, 1, 27, 13, tzinfo=pytz.timezone("UTC")
    )
    assert show_client.show.endtime == datetime(
        2319, 1, 27, 14, tzinfo=pytz.timezone("UTC")
    )
    assert show_client.show.url == "https://www.rabe.ch/stimme-der-kutuesch/"
