from base64 import b64encode
from queue import Queue

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from nowplaying.api import ApiServer


class AuthenticatedClient(Client):
    """An authenticated client for testing."""

    def __init__(self, app, user, password):
        super().__init__(app, Response)
        self.user = user
        self.password = password

    def post(self, *args, **kwargs):
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        if "Authorization" not in kwargs["headers"]:
            kwargs["headers"]["Authorization"] = "Basic {0}".format(
                b64encode(f"{self.user}:{self.password}".encode("utf-8")).decode(
                    "utf-8"
                )
            )
        return super().post(*args, **kwargs)


@pytest.fixture(name="user")
def fixture_user():
    return "user"


@pytest.fixture(name="password")
def fixture_password():
    return "password"


@pytest.fixture(name="users")
def fixture_users(user, password):
    return {user: password}


@pytest.fixture(name="unauthenticated_client")
def fixture_unauthenticated_client(users):
    """Create a test client."""
    event_queue = Queue()
    yield Client(ApiServer(event_queue, users), Response)


@pytest.fixture(name="client")
def fixture_client(users, user, password):
    """Create a test client."""
    event_queue = Queue()
    yield AuthenticatedClient(ApiServer(event_queue, users), user, password)
