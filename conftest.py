import os
import sys

import pytest

from nowplaying.show.show import Show
from nowplaying.track.observers.base import TrackObserver
from nowplaying.track.track import Track

PACKAGE_PARENT = "nowplaying"
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


def new_show(name="Hairmare Traveling Medicine Show"):
    s = Show()
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
    t = Track()
    t.set_artist(artist)
    t.set_title(title)
    t.set_album(album)
    return t


@pytest.fixture()
def track_factory():
    """Return a method to help creating new track objects for tests."""
    return new_track


class DummyObserver(TrackObserver):
    """Shunt class for testing the abstract TrackObserver."""

    pass

    def track_started(self, track):
        pass

    def track_finished(self, track):
        pass


@pytest.fixture()
def dummy_observer():
    return DummyObserver()
