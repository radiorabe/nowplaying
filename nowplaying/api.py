import json
import logging
from queue import Queue

import cherrypy
import cridlib
from cloudevents.exceptions import GenericException as CloudEventException
from cloudevents.http import from_http
from werkzeug.exceptions import BadRequest, HTTPException, UnsupportedMediaType
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

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

    def __init__(self, options, event_queue: Queue, realm: str = "nowplaying"):
        self.options = options
        self.event_queue = event_queue
        self.realm = realm

        self.url_map = Map([Rule("/webhook", endpoint="webhook")])

    def run_server(self):
        """Run the API server."""
        if self.options.debug:
            from werkzeug.serving import run_simple

            self._server = run_simple(
                self.options.apiBindAddress,
                self.options.apiPort,
                self,
                use_debugger=True,
                use_reloader=True,
            )
        else:  # pragma: no cover
            cherrypy.tree.graft(self, "/")
            cherrypy.server.unsubscribe()

            self._server = cherrypy._cpserver.Server()

            self._server.socket_host = self.options.apiBindAddress
            self._server.socket_port = self.options.apiPort

            self._server.subscribe()

            cherrypy.engine.start()
            cherrypy.engine.block()

    def stop_server(self):
        """Stop the server."""
        self._server.stop()
        cherrypy.engine.exit()

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        auth = request.authorization
        if auth and self.check_auth(auth.username, auth.password):
            response = self.dispatch_request(request)
        else:
            response = self.auth_required(request)
        return response(environ, start_response)

    def check_auth(self, username, password):
        return (
            username in self.options.apiAuthUsers
            and self.options.apiAuthUsers[username] == password
        )

    def auth_required(self, request):
        return Response(
            "Could not verify your access level for that URL.\n"
            "You have to login with proper credentials",
            401,
            {"WWW-Authenticate": f'Basic realm="{self.realm}"'},
        )

    def dispatch_request(self, request):
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

    def on_webhook(self, request):
        """Receive a CloudEvent and put it into the event queue."""
        logger.warning("Received a webhook")
        if (
            request.headers.get("Content-Type")
            not in _RABE_CLOUD_EVENTS_SUPPORTED_MEDIA_TYPES
        ):
            raise UnsupportedMediaType()
        try:
            event = from_http(request.headers, request.data)
        except CloudEventException as error:
            raise BadRequest(description=f"{error}")

        try:
            crid = cridlib.parse(event["id"])
            logger.debug("Detected CRID: %s", crid)
        except cridlib.CRIDError as error:
            raise BadRequest(
                description=f"CRID '{event['id']}' is not a RaBe CRID"
            ) from error

        logger.info("Received event: %s", event)

        if event["type"] in _RABE_CLOUD_EVENTS_SUBS:
            self.event_queue.put(event)

        return Response(status="200 Event Received")
