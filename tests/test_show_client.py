"""Tests for :class:`ShowClient`."""

import json
from datetime import datetime
from unittest.mock import Mock

import mock
import pytest
import pytz
import requests

from nowplaying.show.client import ShowClient, ShowClientError

_BASE_URL = "http://example.com/api/live-info-v2/format/json"


def file_get_contents(filename: str) -> str:
    """Read a file and returns its contents."""
    with open(filename) as file:
        return file.read()


def test_init():
    """Test :class:`ShowClient`'s :meth:`.__init__` method."""
    show_client = ShowClient(_BASE_URL)
    assert show_client.current_show_url == _BASE_URL


@mock.patch("requests.get")
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


@mock.patch("requests.get")
def test_update_connection_error(mock_requests_get):
    """Test :class:`ShowClient`'s :meth:`update` method when a connection error occurs.

    It should not crash if external api refuses to connect.
    """
    mock_requests_get.side_effect = requests.exceptions.ConnectionError()
    show_client = ShowClient(_BASE_URL)
    show_client.update()
    assert show_client.show.name is None
    assert show_client.show.url == "https://www.rabe.ch"


@mock.patch("requests.get")
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


@mock.patch("requests.get")
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


@mock.patch("requests.get")
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


@mock.patch("requests.get")
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
    assert show_client.show.name is None
    assert show_client.show.url == "https://www.rabe.ch"
