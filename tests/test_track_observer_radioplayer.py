"""Tests for :class:`RadioplayerTrackObserver`."""

from unittest.mock import Mock, patch

from freezegun import freeze_time

from nowplaying.track.observers.radioplayer import RadioplayerTrackObserver
from nowplaying.track.track import Track

_RADIOPLAYER_URL = "https://ingest.radioplayer.example.org"
# TODO validate this example XML
_EXAMPLE_XML = """<epg xmlns="http://www.radioplayer.co.uk/schemas/11/epgSchedule" xml:lang="de-CH" system="DAB">
  <schedule version="1" creationTime="1993-03-02T00:00:00" originator="https://github.com/radiorabe/nowplaying">
    <scope startTime="1993-03-02T00:00:00+00:00" stopTime="1993-03-02T00:02:08+00:00">
      <serviceScope id="e1.0000.0000.0" radioplayerId="1"/>
    </scope>
    <programme shortId="100" id="crid://rabe.ch/v1/test" recommendation="no" broadcast="on-air" xml:lang="de-CH">
      <ns2:mediumName xmlns:ns2="http://www.radioplayer.co.uk/schemas/11/epgDataTypes" xml:lang="de-CH">RaBe</ns2:mediumName>
      <ns2:longName xmlns:ns2="http://www.radioplayer.co.uk/schemas/11/epgDataTypes" xml:lang="de-CH">Radio Bern RaBe</ns2:longName>
      <ns2:genre xmlns:ns2="http://www.radioplayer.co.uk/schemas/11/epgDataTypes" href="urn:radioplayer:metadata:cs:Category:2012:1" type="main">
        <ns2:name xml:lang="de-CH">Pop/Chart</ns2:name>
      </ns2:genre>
      <ns2:programmeEvent xmlns:ns2="http://www.radioplayer.co.uk/schemas/11/epgDataTypes" shortId="0" id="crid://rabe.ch/v1/test" recommendation="no" broadcast="on-air" xml:lang="de-CH">
        <ns2:mediumName xml:lang="de-CH">An Ode to legacy Python Code</ns2:mediumName>
        <ns2:longName xml:lang="de-CH">An Ode to legacy Python Code</ns2:longName>
        <ns2:mediaCredit role="artist" scheme="urn:ebu">Hairmare and the Band</ns2:mediaCredit>
      </ns2:programmeEvent>
    </programme>
  </schedule>
</epg>
"""


@patch("requests.post")
@patch("cridlib.get")
def test_track_started(
    mock_cridlib_get, mock_requests_post, track_factory, show_factory
):
    """Test :class:`DabAudioCompanionTrackObserver`'s :meth:`track_started` method."""
    # TODO: align return code with ingestor implementation
    mock_requests_post.return_value.getcode = Mock(return_value=200)
    mock_requests_post.return_value.read = Mock(
        # TODO: mock and test real return value
        return_value="contents"
    )
    mock_cridlib_get.return_value = "crid://rabe.ch/v1/test"

    track = track_factory()
    track.show = show_factory()

    # if it's disabled
    radioplayer_track_observer = RadioplayerTrackObserver(
        RadioplayerTrackObserver.Options(enabled=False, url=_RADIOPLAYER_URL)
    )
    assert radioplayer_track_observer.track_started(Track()) is None

    # reset system under test
    radioplayer_track_observer = RadioplayerTrackObserver(
        RadioplayerTrackObserver.Options(enabled=True, url=_RADIOPLAYER_URL)
    )

    # check that short tracks dont get sent
    track = track_factory(artist="Radio Bern", title="Livestream", duration=3)
    mock_requests_post.reset_mock()
    radioplayer_track_observer.track_started(track)
    mock_requests_post.assert_not_called()

    # check that default tracks dont get sent
    track = track_factory(artist="Radio Bern", title="Livestream", duration=60)
    mock_requests_post.reset_mock()
    radioplayer_track_observer.track_started(track)
    mock_requests_post.assert_not_called()

    # check that we send nice data to the right endpoint
    with freeze_time("1993-03-02 00:00:00 UTC"):
        track = track_factory()
        radioplayer_track_observer.track_started(track)
    mock_requests_post.assert_called_once()
    mock_requests_post.assert_called_with(
        f"{_RADIOPLAYER_URL}/ingestor/metadata/v1/np/",
        headers={"Content-Type": "application/xml"},
        data=_EXAMPLE_XML,
    )


def test_track_finished():
    """Test :class:`RadioplayerTrackObserver`'s :meth:`track_finished` method."""
    radioplayer_track_observer = RadioplayerTrackObserver(
        RadioplayerTrackObserver.Options(enabled=True, url=_RADIOPLAYER_URL)
    )
    assert radioplayer_track_observer.track_finished(Track())
