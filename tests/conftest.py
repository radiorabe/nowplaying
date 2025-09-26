from base64 import b64encode
from queue import Queue
from types import SimpleNamespace

import pytest
from faker import Faker
from werkzeug.test import Client
from werkzeug.wrappers import Response

from nowplaying.api import ApiServer
from nowplaying.show.show import Show
from nowplaying.track.observers.base import TrackObserver
from nowplaying.track.track import Track


class AuthenticatedClient(Client):
    """An authenticated client for testing."""

    def __init__(self, app, user, password):
        super().__init__(app, Response)
        self.user = user
        self.password = password

    def post(self, *args, **kwargs):
        if "headers" not in kwargs:  # pragma: no cover
            kwargs["headers"] = {}
        if "Authorization" not in kwargs["headers"]:
            pwd = b64encode(f"{self.user}:{self.password}".encode()).decode("utf-8")
            kwargs["headers"]["Authorization"] = f"Basic {pwd}"
        return super().post(*args, **kwargs)


@pytest.fixture(name="user")
def fixture_user():
    return Faker().user_name()


@pytest.fixture(name="password")
def fixture_password():
    return Faker().password()


@pytest.fixture(name="users")
def fixture_users(user, password):
    return {user: password}


@pytest.fixture(name="options")
def fixture_options(users):
    return SimpleNamespace(
        api_auth_users=users,
    )


@pytest.fixture(name="unauthenticated_client")
def fixture_unauthenticated_client(options):
    """Create a test client."""
    return Client(ApiServer(options, event_queue=Queue()), Response)


@pytest.fixture(name="client")
def fixture_client(options, user, password):
    """Create a test client."""
    return AuthenticatedClient(ApiServer(options, event_queue=Queue()), user, password)


def new_show(name="Hairmare Traveling Medicine Show"):
    s = Show()
    s.set_name(name)
    return s


@pytest.fixture
def show_factory():
    """Return a method to help creating new show objects for tests."""
    return new_show


def new_track(
    artist="Hairmare and the Band",
    title="An Ode to legacy Python Code",
    album="Live at the Refactoring Club",
    duration=128,
):
    t = Track()
    t.set_artist(artist)
    t.set_title(title)
    t.set_album(album)
    t.set_duration(duration)
    return t


@pytest.fixture
def track_factory():
    """Return a method to help creating new track objects for tests."""
    return new_track


class DummyObserver(TrackObserver):
    """Shunt class for testing the abstract TrackObserver."""

    def track_started(self, track):
        pass

    def track_finished(self, track):
        pass


@pytest.fixture
def dummy_observer():
    return DummyObserver()
