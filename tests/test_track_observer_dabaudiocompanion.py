"""Tests for :class:`DabAudioCompanionTrackObserver`."""

from unittest.mock import MagicMock, Mock, patch

from nowplaying.track.observers.dab_audio_companion import (
    DabAudioCompanionTrackObserver,
)
from nowplaying.track.track import Track

_BASE_URL = "http://localhost:80"


def test_init():
    """Test class:`DabAudioCompanionTrackObserver`'s :meth:`.__init__` method."""
    dab_audio_companion_track_observer = DabAudioCompanionTrackObserver(
        options=DabAudioCompanionTrackObserver.Options(
            url=_BASE_URL,
        )
    )
    assert dab_audio_companion_track_observer.base_url == f"{_BASE_URL}/api/setDLS"


@patch("requests.post")
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
        options=DabAudioCompanionTrackObserver.Options(
            url=_BASE_URL,
        )
    )
    # assume that last frame was DL+ on startup so we always send
    # delete tags when a show w/o dl+ starts
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
    mock_requests_post.reset_mock()
    dab_audio_companion_track_observer.track_started(track)
    assert not dab_audio_companion_track_observer.last_frame_was_dl_plus
    mock_requests_post.assert_called_once()
    args, _ = mock_requests_post.call_args
    assert args[0] == f"{_BASE_URL}/api/setDLS"
    results = args[1]["dls"].split("\n")
    assert results[0] == "##### parameters { #####"
    assert results[len(results) - 2] == "##### parameters } #####"
    expected = [
        "##### parameters { #####",
        "DL_PLUS=1",
        "DL_PLUS_TAG=1 5 0",  # delete ITEM.TITLE
        "DL_PLUS_TAG=32 0 10",  # add STATIONNAME.LONG
        "DL_PLUS_TAG=4 5 0",  # delete ITEM.ARTIST
        "##### parameters } #####",
        "Radio Bern - Hairmare Traveling Medicine Show",
    ]
    expected.sort()
    results.sort()
    assert all([a == b for a, b in zip(results, expected)])

    # once ITEM delete have been sent we send regular DLS again
    dab_audio_companion_track_observer.track_started(track)
    assert not dab_audio_companion_track_observer.last_frame_was_dl_plus
    mock_requests_post.assert_called_with(
        f"{_BASE_URL}/api/setDLS",
        {"dls": "Radio Bern - Hairmare Traveling Medicine Show"},
    )

    # check that short tracks dont get sent
    track = track_factory(artist="Radio Bern", title="Livestream", duration=3)
    mock_requests_post.reset_mock()
    dab_audio_companion_track_observer.track_started(track)
    mock_requests_post.assert_not_called()


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

    o = DabAudioCompanionTrackObserver(
        options=DabAudioCompanionTrackObserver.Options(
            url=_BASE_URL,
            dl_plus=False,
        )
    )
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
        options=DabAudioCompanionTrackObserver.Options(
            url=_BASE_URL,
        )
    )
    assert dab_audio_companion_track_observer.track_finished(Track())
