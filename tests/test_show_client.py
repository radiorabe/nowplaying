import json
from datetime import datetime
from unittest.mock import Mock

import mock
import pytest
import pytz
import requests

from nowplaying.show import client


def file_get_contents(filename):
    with open(filename) as f:
        return f.read()


class TestShowClient:
    def test_init(self):
        s = client.ShowClient("http://example.com/api/live-info-v2/format/json")
        assert s.current_show_url == "http://example.com/api/live-info-v2/format/json"

    @mock.patch("requests.get")
    def test_update(self, mock_requests_get):
        mock_requests_get.return_value.json = Mock(
            return_value=json.loads(
                file_get_contents("tests/fixtures/cast_now_during_show.json")
            )
        )
        s = client.ShowClient("http://example.com/api/live-info-v2/format/json")
        s.update()
        assert s.show.name == "Voice of Hindu Kush"
        assert s.show.starttime == datetime(
            2019, 1, 27, 13, tzinfo=pytz.timezone("UTC")
        )
        assert s.show.endtime == datetime(2319, 1, 27, 14, tzinfo=pytz.timezone("UTC"))
        assert s.show.url == "https://www.rabe.ch/stimme-der-kutuesch/"

    @mock.patch("requests.get")
    def test_update_connection_error(self, mock_requests_get):
        """Don't crash if external api refuses to connect."""
        mock_requests_get.side_effect = requests.exceptions.ConnectionError()
        s = client.ShowClient("http://example.com/api/live-info-v2/format/json")
        s.update()
        assert s.show.name is None
        assert s.show.url == "https://www.rabe.ch"

    @mock.patch("requests.get")
    def test_update_no_url(self, mock_requests_get):
        mock_requests_get.return_value.json = Mock(
            return_value=json.loads(
                file_get_contents("tests/fixtures/cast_now_no_url.json")
            )
        )
        s = client.ShowClient("http://example.com/api/live-info-v2/format/json")
        s.update()
        assert s.show.url == "https://www.rabe.ch"

    @mock.patch("requests.get")
    @pytest.mark.parametrize(
        "fixture,field",
        [
            ("cast_now_no_name", "name"),
            ("cast_now_no_end", "end time"),
            ("cast_now_no_start", "start time"),
        ],
    )
    def test_update_empty_field(self, mock_requests_get, fixture, field):
        mock_requests_get.return_value.json = Mock(
            return_value=json.loads(file_get_contents(f"tests/fixtures/{fixture}.json"))
        )
        s = client.ShowClient("http://example.com/api/live-info-v2/format/json")
        with pytest.raises(client.ShowClientError) as info:
            s.update()
        assert str(info.value) == f"Missing show {field}"

    @mock.patch("requests.get")
    def test_update_past_show(self, mock_requests_get):
        mock_requests_get.return_value.json = Mock(
            return_value=json.loads(
                file_get_contents("tests/fixtures/cast_now_past_show.json")
            )
        )
        s = client.ShowClient("http://example.com/api/live-info-v2/format/json")
        with pytest.raises(client.ShowClientError) as info:
            s.update()
        assert (
            str(info.value)
            == "Show end time (2019-01-27 14:00:00+00:00) is in the past"
        )

    @mock.patch("requests.get")
    def test_update_show_empty(self, mock_requests_get):
        """Should not crash if external api has no info."""
        mock_requests_get.return_value.json = Mock(
            return_value=json.loads(
                file_get_contents("tests/fixtures/cast_now_show_empty.json")
            )
        )
        s = client.ShowClient("http://example.com/api/live-info-v2/format/json")
        s.update()
        assert s.show.name is None
        assert s.show.url == "https://www.rabe.ch"
