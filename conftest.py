import pytest

from nowplaying.show import show
from nowplaying.track import track


def new_show(name="Hairmare Traveling Medicine Show"):
    s = show.Show()
    s.set_name("Hairmare Traveling Medicine Show")
    return s


@pytest.fixture()
def show_factory():
    """Return a method to help creating new show objects for tests."""
    return new_show


def new_track(
    artist="Hairmare and the Band",
    title="An Ode to legacy Python Code",
    album="Live at the Refactoring Club",
):
    t = track.Track()
    t.set_artist(artist)
    t.set_title(title)
    t.set_album(album)
    return t


@pytest.fixture()
def track_factory():
    """Return a method to help creating new track objects for tests."""
    return new_track
