"""Tests for :class:`DabAudioCompanionTrackObserver`."""

from unittest.mock import Mock

import mock

from nowplaying.track.observer import DabAudioCompanionTrackObserver
from nowplaying.track.track import Track

_BASE_URL = "http://localhost:80"


def test_init():
    """Test class:`DabAudioCompanionTrackObserver`'s :meth:`.__init__` method."""
    dab_audio_companion_track_observer = DabAudioCompanionTrackObserver(
        baseUrl=_BASE_URL
    )
    assert dab_audio_companion_track_observer.baseUrl == f"{_BASE_URL}/api/setDLS"


@mock.patch("requests.get")
def test_track_started(mock_requests_get, track_factory, show_factory):
    """Test :class:`DabAudioCompanionTrackObserver`'s :meth:`track_started` method."""
    mock_requests_get.return_value.getcode = Mock(return_value=200)
    mock_requests_get.return_value.read = Mock(
        # TODO: mock and test real return value
        return_value="contents"
    )

    track = track_factory()
    track.show = show_factory()

    dab_audio_companion_track_observer = DabAudioCompanionTrackObserver(
        baseUrl=_BASE_URL
    )
    dab_audio_companion_track_observer.track_started(track)

    mock_requests_get.assert_called_with(
        f"{_BASE_URL}/api/setDLS",
        {"artist": "Hairmare and the Band", "title": "An Ode to legacy Python Code"},
    )

    track = track_factory(artist="Radio Bern", title="Livestream")
    track.show = show_factory()

    dab_audio_companion_track_observer.track_started(track)
    mock_requests_get.assert_called_with(
        f"{_BASE_URL}/api/setDLS",
        {"dls": "Radio Bern - Hairmare Traveling Medicine Show"},
    )


def test_track_finished():
    """Test :class:`DabAudioCompanionTrackObserver`'s :meth:`track_finished` method."""
    dab_audio_companion_track_observer = DabAudioCompanionTrackObserver(
        baseUrl=_BASE_URL
    )
    assert dab_audio_companion_track_observer.track_finished(Track())
