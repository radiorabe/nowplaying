import pytest
from cloudevents.http.event import CloudEvent
from mock import Mock, patch

from nowplaying.input.observer import KlangbeckenInputObserver
from nowplaying.track.track import Track


@pytest.fixture(name="event")
def fixture_event() -> CloudEvent:
    return CloudEvent(
        attributes={
            "type": "ch.rabe.api.events.track.v1.trackStarted",
            "source": "http://www.rabe.ch/klangbecken/",
        },
        data={
            "item.artist": "Peaches",
            "item.title": "Fuck the Pain Away",
        },
    )


@pytest.mark.skip("TODO: test once input file is replaced with api")
def test_init():
    show_url = "http://www.rabe.ch/klangbecken/"
    observer = KlangbeckenInputObserver(show_url, "tests/fixtures/now-playing.xml")

    assert observer.current_show_url == show_url


@patch("nowplaying.show.client.ShowClient.get_show_info")
@pytest.mark.parametrize(
    "saemubox_id,expected", [(1, True), (2, False), (0, False), (-1, False)]
)
def test_handle_id(mock_get_show_info, saemubox_id, expected, event: CloudEvent):
    show_url = "http://www.rabe.ch/klangbecken/"
    observer = KlangbeckenInputObserver(show_url, "tests/fixtures/now-playing.xml")

    mock_get_show_info.assert_called_once()

    assert observer.handle_id(saemubox_id, event) == expected

    event["type"] = "ch.rabe.api.events.track.v1.trackFinished"
    assert observer.handle_id(saemubox_id, event) == expected


@patch("nowplaying.show.client.ShowClient.get_show_info")
def test_handle(mock_get_show_info):
    show_url = "http://www.rabe.ch/klangbecken/"
    mock_track_handler = Mock()

    observer = KlangbeckenInputObserver(show_url, "tests/fixtures/now-playing.xml")
    mock_get_show_info.assert_called_once()
    assert observer.first_run

    mock_get_show_info.reset_mock()

    observer.add_track_handler(mock_track_handler)
    observer.handle()

    assert not observer.first_run
    mock_get_show_info.assert_called_once()


def test_parse_event(event: CloudEvent):
    expected_track = Track()
    expected_track.artist = "Peaches"
    expected_track.title = "Fuck the Pain Away"

    observer = KlangbeckenInputObserver(
        "http://example.org/klangbecken/", "tests/fixtures/now-playing.xml"
    )

    track = observer.parse_event(event)

    assert track.artist == expected_track.artist
    assert track.title == expected_track.title

    event["type"] = "ch.rabe.api.events.track.v1.trackFinished"
    track = observer.parse_event(event)

    assert track.artist == expected_track.artist
    assert track.title == expected_track.title
