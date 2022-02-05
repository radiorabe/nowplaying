"""Test the werkzeug based api server."""

import json
from queue import Queue
from types import SimpleNamespace

import mock
import pytest

from nowplaying.api import ApiServer

_WEBHOOK_ENDPOINT = "/webhook"
_CONTENT_TYPE_JSON = "application/json"
_CONTENT_TYPE_CLOUDEVENTS = "application/cloudevents+json"


@mock.patch("werkzeug.serving.run_simple")
def test_run_server_with_debug(mock_run_simple, users):
    """Test the run_server function."""
    mock_run_simple.return_value = None
    mock_run_simple.side_effect = None

    options = SimpleNamespace(
        **{
            "apiBindAddress": "0.0.0.0",
            "apiPort": 8080,
            "apiAuthUsers": users,
            "debug": True,
        }
    )
    event_queue = Queue()

    server = ApiServer(options, event_queue=event_queue)
    server.run_server()
    mock_run_simple.assert_called_once_with(
        options.apiBindAddress,
        options.apiPort,
        mock.ANY,
        use_debugger=True,
        use_reloader=True,
    )


@mock.patch("cherrypy.engine.stop")
@mock.patch("cherrypy._cpserver.Server")
def test_stop_server(mock_server, mock_stop, options):
    """Test the stop_server function."""

    api = ApiServer(options, event_queue=Queue())
    api._server = mock_server
    api.stop_server()

    mock_server.stop.assert_called_once_with()
    mock_stop.assert_called_once_with()


@pytest.mark.parametrize("content_type", [None, "text/plain", "application/xml"])
def test_webhook_no_supported_header(client, content_type):
    """Test the webhook function with invalid headers."""
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    resp = client.post(_WEBHOOK_ENDPOINT, headers=headers, data="{}")
    assert resp.status_code == 415
    assert (
        resp.data.decode("utf-8")
        == '"The server does not support the media type transmitted in the request."'
    )


@pytest.mark.parametrize(
    "content_type", [_CONTENT_TYPE_JSON, _CONTENT_TYPE_CLOUDEVENTS]
)
def test_webhook_invalid_body(client, content_type):
    """Test the webhook function with invalid JSON."""
    body = "invalid-json"
    resp = client.post(
        _WEBHOOK_ENDPOINT, data=body, headers={"Content-Type": content_type}
    )
    assert resp.status_code == 400
    assert resp.data.decode("utf-8") == json.dumps(
        """Failed to read specversion from both headers and data. The following can not be parsed as json: b'invalid-json'"""
    )


@pytest.mark.parametrize(
    "content_type,body,expected_status",
    [
        (
            _CONTENT_TYPE_JSON,
            {"content": "is not a valid event but is valid json"},
            "Failed to find specversion in HTTP request",
        ),
        (
            _CONTENT_TYPE_CLOUDEVENTS,
            {"specversion": "2.0"},
            "Found invalid specversion 2.0",
        ),
        (
            _CONTENT_TYPE_CLOUDEVENTS,
            {"specversion": "1.0", "type": "ch.rabe.api.events.track.v1.trackStarted"},
            "Missing required attributes: {'",  # {'source', 'id'} but in flaky order
        ),
    ],
)
def test_webhook_invalid_event(client, content_type, body, expected_status):
    """Test the webhook function."""
    resp = client.post(
        _WEBHOOK_ENDPOINT, data=json.dumps(body), headers={"Content-Type": content_type}
    )
    assert resp.status_code == 400
    assert expected_status in resp.data.decode("utf-8")


@pytest.mark.parametrize(
    "content_type", [_CONTENT_TYPE_JSON, _CONTENT_TYPE_CLOUDEVENTS]
)
def test_webhook_valid_event(client, content_type):
    """Test the webhook function."""
    body = json.dumps(
        {
            "specversion": "1.0",
            "type": "ch.rabe.api.events.track.v1.trackStarted",
            "source": "https://rabe.ch",
            "id": "12345",
        }
    )
    assert client.application.event_queue.qsize() == 0
    resp = client.post(
        _WEBHOOK_ENDPOINT, data=body, headers={"Content-Type": content_type}
    )
    assert resp.status_code == 200
    assert resp.status == "200 Event Received"
    assert client.application.event_queue.qsize() == 1
    event = client.application.event_queue.get()
    assert event["source"] == "https://rabe.ch"
    assert event["id"] == "12345"
    assert event["type"] == "ch.rabe.api.events.track.v1.trackStarted"


def test_webhook_auth_fail(unauthenticated_client):
    """Test the webhook function."""
    resp = unauthenticated_client.post(
        _WEBHOOK_ENDPOINT, data="{}", headers={"Content-Type": _CONTENT_TYPE_JSON}
    )
    assert resp.status_code == 401
    assert resp.status == "401 UNAUTHORIZED"
