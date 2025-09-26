"""Nowplaying ApiServer."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Self

import cherrypy  # type: ignore[import-untyped]
import cridlib
from cloudevents.exceptions import GenericException as CloudEventException
from cloudevents.http import from_http
from werkzeug.exceptions import BadRequest, HTTPException, UnsupportedMediaType
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from queue import Queue
    from wsgiref.types import StartResponse, WSGIEnvironment

    from nowplaying.options import Options


logger = logging.getLogger(__name__)

_RABE_CLOUD_EVENTS_SUBS = (
    "ch.rabe.api.events.track.v1.trackStarted",
    "ch.rabe.api.events.track.v1.trackFinished",
)
_RABE_CLOUD_EVENTS_SUPPORTED_MEDIA_TYPES = (
    "application/cloudevents+json",
    "application/json",
)


class ApiServer:
    """The API server."""

    def __init__(
        self: Self,
        options: Options,
        event_queue: Queue,
        realm: str = "nowplaying",
    ) -> None:
        """Create ApiServer."""
        self.options = options
        self.event_queue = event_queue
        self.realm = realm

        self.url_map = Map([Rule("/webhook", endpoint="webhook")])

    def run_server(self: Self) -> None:
        """Run the API server."""
        if self.options.debug:
            from werkzeug.serving import run_simple  # noqa: PLC0415

            run_simple(
                self.options.api_bind_address,
                self.options.api_port,
                self,
                use_debugger=True,
                use_reloader=True,
            )
        else:  # pragma: no cover
            cherrypy.tree.graft(self, "/")
            cherrypy.server.unsubscribe()

            self._server = cherrypy._cpserver.Server()  # noqa: SLF001

            self._server.socket_host = self.options.api_bind_address
            self._server.socket_port = self.options.api_port

            self._server.subscribe()

            cherrypy.engine.start()
            cherrypy.engine.block()

    def stop_server(self: Self) -> None:
        """Stop the server."""
        self._server.stop()
        cherrypy.engine.exit()

    def __call__(
        self: Self,
        environ: WSGIEnvironment,
        start_response: StartResponse,
    ) -> Iterable[bytes]:
        """Forward calls to wsgi_app."""
        return self.wsgi_app(environ, start_response)

    def wsgi_app(
        self: Self,
        environ: WSGIEnvironment,
        start_response: StartResponse,
    ) -> Iterable[bytes]:
        """Return a wsgi app."""
        request = Request(environ)
        auth = request.authorization
        if auth and self.check_auth(auth.username, auth.password):
            response = self.dispatch_request(request)
        else:
            response = self.auth_required(request)
        return response(environ, start_response)

    def check_auth(self: Self, username: str | None, password: str | None) -> bool:
        """Check if auth is valid."""
        return str(
            username,
        ) in self.options.api_auth_users and self.options.api_auth_users[
            str(username)
        ] == str(
            password,
        )

    def auth_required(self: Self, _: Request) -> Response:
        """Check if auth is required."""
        return Response(
            "Could not verify your access level for that URL.\n"
            "You have to login with proper credentials",
            401,
            {"WWW-Authenticate": f'Basic realm="{self.realm}"'},
        )

    def dispatch_request(self: Self, request: Request) -> Response | HTTPException:
        """Dispatch requests to handlers."""
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"on_{endpoint}")(request, **values)
        except HTTPException as e:
            return Response(
                json.dumps(e.description),
                e.code,
                {"Content-Type": "application/json"},
            )

    def on_webhook(self: Self, request: Request) -> Response:
        """Receive a CloudEvent and put it into the event queue."""
        logger.warning("Received a webhook")
        if (
            request.headers.get("Content-Type")
            not in _RABE_CLOUD_EVENTS_SUPPORTED_MEDIA_TYPES
        ):
            raise UnsupportedMediaType
        try:
            event = from_http(request.headers, request.data)  # type: ignore[arg-type]
        except CloudEventException as error:
            raise BadRequest(description=str(error)) from error

        try:
            crid = cridlib.parse(event["id"])
            logger.debug("Detected CRID: %s", crid)
        except cridlib.CRIDError as error:
            raise BadRequest(
                description=f"CRID '{event['id']}' is not a RaBe CRID",
            ) from error

        logger.info("Received event: %s", event)

        if event["type"] in _RABE_CLOUD_EVENTS_SUBS:
            self.event_queue.put(event)

        return Response(status="200 Event Received")
