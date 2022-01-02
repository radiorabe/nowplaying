import pytest
from cloudevents.http.event import CloudEvent
from isodate import parse_datetime

from nowplaying.input.observer import KlangbeckenInputObserver
from nowplaying.track.handler import TrackEventHandler


@pytest.mark.parametrize(
    "source, expected",
    [
        ("https://github/radiorabe/klangbecken", True),
        ("https://github/radiorabe/something-that-is-not-klangbecken", False),
    ],
)
def test_klangbecken_input_observer_handles(source, expected):
    """Test the KlangbeckenInputObserver handles function."""
    observer = KlangbeckenInputObserver(current_show_url="https://example.org")
    event = CloudEvent(
        attributes={
            "specversion": "1.0",
            "type": "ch.rabe.api.events.track.v1.trackStarted",
            "source": source,
            "id": "my-id",
        },
    )
    assert observer.handles(event) == expected


def test_klangbecken_input_observer_event():
    """Test the KlangbeckenInputObserver event function."""
    observer = KlangbeckenInputObserver(current_show_url="https://example.org")
    observer.add_track_handler(TrackEventHandler())
    event = CloudEvent(
        attributes={
            "specversion": "1.0",
            "type": "ch.rabe.api.events.track.v1.trackStarted",
            "source": "https://github.com/radiorabe.klangbecken",
            "id": "my-id",
            "time": "2020-01-01T00:00:00Z",
        },
        data={"item.artist": "artist", "item.title": "title"},
    )
    observer.event(event)
    # TODO assert something


def test_klangbecken_input_observer_parse_event():
    """Test the KlangbeckenInputObserver parse_event function."""
    observer = KlangbeckenInputObserver(current_show_url="https://example.org")
    observer.add_track_handler(TrackEventHandler())
    event = CloudEvent(
        attributes={
            "specversion": "1.0",
            "type": "ch.rabe.api.events.track.v1.trackStarted",
            "source": "https://github.com/radiorabe.klangbecken",
            "id": "my-id",
            "time": "2020-01-01T00:00:00Z",
        },
        data={"item.artist": "artist", "item.title": "title", "item.length": 60},
    )
    track = observer.parse_event(event)
    assert track.artist == "artist"
    assert track.title == "title"
    assert track.endtime == parse_datetime("2020-01-01T00:01:00Z")
