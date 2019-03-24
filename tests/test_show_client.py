from datetime import datetime

import mock
import pytest
import pytz

from nowplaying.show import client


class TestShowClient:
    def test_init(self):
        s = client.ShowClient("http://example.com")
        assert s.current_show_url == "http://example.com"

    @mock.patch("urllib.request.urlopen")
    def test_update(self, mock_urlopen):
        mock_urlopen.return_value = "tests/fixtures/cast_now_during_show.xml"
        s = client.ShowClient("http://example.com")
        s.update()
        assert s.show.name == "Voice of Hindu Kush"
        assert s.show.starttime == datetime(
            2019, 1, 27, 13, tzinfo=pytz.timezone("UTC")
        )
        assert s.show.endtime == datetime(2319, 1, 27, 14, tzinfo=pytz.timezone("UTC"))
        assert s.show.url == "https://www.rabe.ch/stimme-der-kutuesch/"

    @mock.patch("urllib.request.urlopen")
    def test_update_no_url(self, mock_urlopen):
        mock_urlopen.return_value = "tests/fixtures/cast_now_no_url.xml"
        s = client.ShowClient("http://example.com")
        s.update()
        assert s.show.url == "https://www.rabe.ch"

    @mock.patch("urllib.request.urlopen")
    def test_update_past_show(self, mock_urlopen):
        mock_urlopen.return_value = "tests/fixtures/cast_now_past_show.xml"
        s = client.ShowClient("http://example.com")
        with pytest.raises(client.ShowClientError) as info:
            s.update()
        assert (
            str(info.value)
            == "Show end time (2019-01-27 14:00:00+00:00) is in the past"
        )
