import json
import logging
from queue import Queue

import cherrypy
import isodate
from cloudevents.exceptions import GenericException as CloudEventException
from cloudevents.http import from_http

logger = logging.getLogger(__name__)

_RABE_CLOUD_EVENTS_SUBS = (
    "ch.rabe.api.events.track.v1.trackStarted",
    "ch.rabe.api.events.track.v1.trackFinished",
)


class ApiServer:
    """The API server."""

    def __init__(self, event_queue: Queue):
        self.event_queue = event_queue

    @cherrypy.expose
    @cherrypy.tools.json_in(
        content_type=("application/json", "application/cloudevents+json")
    )
    def webhook(self):
        """Receive a CloudEvent and put it into the event queue."""
        try:
            event = from_http(
                cherrypy.request.headers, json.dumps(cherrypy.request.json)
            )
        except CloudEventException as error:
            cherrypy.response.status = f"400 {error}"
            return

        logger.info("Received event: %s", event)

        if event["time"]:
            event["time"] = isodate.parse_datetime(event["time"])
        if event["type"] in _RABE_CLOUD_EVENTS_SUBS:
            self.event_queue.put(event)

        cherrypy.response.status = "204 Event Received"
