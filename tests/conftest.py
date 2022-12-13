from base64 import b64encode
from queue import Queue
from types import SimpleNamespace

import pytest
from faker import Faker
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
        **{
            "apiAuthUsers": users,
        }
    )


@pytest.fixture(name="unauthenticated_client")
def fixture_unauthenticated_client(options):
    """Create a test client."""
    yield Client(ApiServer(options, event_queue=Queue()), Response)


@pytest.fixture(name="client")
def fixture_client(options, user, password):
    """Create a test client."""
    yield AuthenticatedClient(ApiServer(options, event_queue=Queue()), user, password)
