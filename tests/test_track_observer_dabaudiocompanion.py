"""Tests for :class:`DabAudioCompanionTrackObserver`."""

from unittest.mock import Mock

import mock
from mock.mock import MagicMock, patch

from nowplaying.track.observers.dab_audio_companion import (
    DabAudioCompanionTrackObserver,
)
from nowplaying.track.track import Track

_BASE_URL = "http://localhost:80"


def test_init():
    """Test class:`DabAudioCompanionTrackObserver`'s :meth:`.__init__` method."""
    dab_audio_companion_track_observer = DabAudioCompanionTrackObserver(
        base_url=_BASE_URL
    )
    assert dab_audio_companion_track_observer.base_url == f"{_BASE_URL}/api/setDLS"


@mock.patch("requests.post")
def test_track_started(mock_requests_post, track_factory, show_factory):
    """Test :class:`DabAudioCompanionTrackObserver`'s :meth:`track_started` method."""
    mock_requests_post.return_value.getcode = Mock(return_value=200)
    mock_requests_post.return_value.read = Mock(
        # TODO: mock and test real return value
        return_value="contents"
    )

    track = track_factory()
    track.show = show_factory()

    dab_audio_companion_track_observer = DabAudioCompanionTrackObserver(
        base_url=_BASE_URL, dls_enabled=True
    )
    # assume that last frame was DL+ on startup so we always send delete tags when a show w/o dl+ starts
    assert dab_audio_companion_track_observer.last_frame_was_dl_plus

    # We send DLS+ if is is available and enabled
    dab_audio_companion_track_observer.track_started(track)
    assert dab_audio_companion_track_observer.last_frame_was_dl_plus
    mock_requests_post.assert_called_with(
        f"{_BASE_URL}/api/setDLS",
        {"artist": "Hairmare and the Band", "title": "An Ode to legacy Python Code"},
    )

    track = track_factory(artist="Radio Bern", title="Livestream")
    track.show = show_factory()

    # when we first send DLS after having sent DLS+ we expect some delete tags
    dab_audio_companion_track_observer.track_started(track)
    assert not dab_audio_companion_track_observer.last_frame_was_dl_plus
    mock_requests_post.assert_called_with(
        f"{_BASE_URL}/api/setDLS",
        {
            "dls": "".join(
                (
                    "##### parameters { #####\n",
                    "DL_PLUS=1\n",
                    "DL_PLUS_TAG=1 5 0\n",
                    "DL_PLUS_TAG=4 5 0\n",
                    "##### parameters } #####\n",
                    "Radio Bern - Hairmare Traveling Medicine Show",
                )
            )
        },
    )

    # once ITEM delete have been sent we send regular DLS again
    dab_audio_companion_track_observer.track_started(track)
    assert not dab_audio_companion_track_observer.last_frame_was_dl_plus
    mock_requests_post.assert_called_with(
        f"{_BASE_URL}/api/setDLS",
        {"dls": "Radio Bern - Hairmare Traveling Medicine Show"},
    )


@patch("urllib.request.urlopen")
def test_track_started_plain(mock_urlopen, track_factory, show_factory):
    # TODO v3 remove when we drop plain support
    cm = MagicMock()
    cm.getcode.return_value = 200
    # TODO: mock and test real return value
    cm.read.return_value = "contents"
    cm.__enter__.return_value = cm
    mock_urlopen.return_value = cm

    track = track_factory()
    track.show = show_factory()

    o = DabAudioCompanionTrackObserver(base_url="http://localhost:80")
    # last frame cannot be dl+ since the feature is inactive
    assert not o.last_frame_was_dl_plus

    o.track_started(track)
    assert not o.last_frame_was_dl_plus
    mock_urlopen.assert_called_with(
        "http://localhost:80/api/setDLS?dls=b%27Hairmare+and+the+Band%27+-+b%27An+Ode+to+legacy+Python+Code%27"
    )

    track = track_factory(artist="Radio Bern", title="Livestream")
    track.show = show_factory()

    o.track_started(track)
    mock_urlopen.assert_called_with(
        "http://localhost:80/api/setDLS?dls=b%27Radio+Bern%27+-+b%27Hairmare+Traveling+Medicine+Show%27"
    )


def test_track_finished():
    """Test :class:`DabAudioCompanionTrackObserver`'s :meth:`track_finished` method."""
    dab_audio_companion_track_observer = DabAudioCompanionTrackObserver(
        base_url=_BASE_URL
    )
    assert dab_audio_companion_track_observer.track_finished(Track())
