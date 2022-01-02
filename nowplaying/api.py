import json
import logging
from queue import Queue

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

    @classmethod
    def run_server(cls, options, event_queue: Queue):
        """Run the API server."""
        app = cls(event_queue, options.apiAuthUsers)
        if options.debug:
            from werkzeug.serving import run_simple

            run_simple(
                options.apiBindAddress,
                options.apiPort,
                app,
                use_debugger=True,
                use_reloader=True,
            )
        else:  # pragma: no cover
            import cherrypy

            cherrypy.tree.graft(app, "/")
            cherrypy.server.unsubscribe()

            server = cherrypy._cpserver.Server()

            server.socket_host = options.apiBindAddress
            server.socket_port = options.apiPort

            server.subscribe()

            cherrypy.engine.start()
            cherrypy.engine.block()

    def __init__(self, event_queue: Queue, users: dict, realm: str = "nowplaying"):
        self.event_queue = event_queue
        self.users = users
        self.realm = realm

        self.url_map = Map([Rule("/webhook", endpoint="webhook")])

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        auth = request.authorization
        if not auth or not self.check_auth(auth.username, auth.password):
            response = self.auth_required(request)
        else:
            response = self.dispatch_request(request)
        return response(environ, start_response)

    def check_auth(self, username, password):
        return username in self.users and self.users[username] == password

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

        logger.info("Received event: %s", event)

        if event["type"] in _RABE_CLOUD_EVENTS_SUBS:
            self.event_queue.put(event)

        return Response(status="200 Event Received")
