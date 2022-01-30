# Radio Bern Now Playing

This repo contains the tool we use to grab, aggregate and publish show, artist and track metadata from various sources.

The nowplaying project grabs info from RaBes playout solution and publishes them to broadcast vectors like DAB+ and Webstreams.

## Usage

TBD

### RaBe CloudEvents

nowplaying consumes [RaBe CloudEvents](https://github.com/radiorabe/event-spec) and reacts to them depending on the event type and source.

If you need to send events to nowplaying, you can use the following examples that are based on the same [python-sdk](https://github.com/cloudevents/sdk-python) nowplaying uses. The same can be acheived with any client that can send POST requests and headers, see the cURL example below for a simple bash example that demonstrates how the request works.

```python
import requests

from cloudevents.http import CloudEvent, to_structured

def send_event(url, username, password):
    # This data defines a cloudevent
    attributes = {
        "specversion": "1.0",
        # as defined by the events-spec repo
        "type": "ch.rabe.api.events.track.v1.trackStarted",
        # for klangbecken the github link is always used as source (as per events-spec)
        "source": "https://github.com/radiorabe/klangbecken",
        # this should be generated and could/should point to a real
        # URL on either https://klangbecken.service.int.example.org
        # using a `crid://` URL based on the upcoming crid-spec.
        "id": "uri:demo:12345",
    }
    data = {
        "item.title": "Track Title",
        "item.artist": "Artist",
        # length in seconds, optional if you also implement sending the
        # not "completely specced yet" trackFinished event
        "item.length": 60,
    }

    event = CloudEvent(attributes, data)
    headers, body = to_structured(event)

    # send and print event
    requests.post(url, headers=headers, data=body, auth=(username, password))
    print(f"Sent {event['id']} from {event['source']} with {event.data}")

if __name__ == "__main__":
    # local config
    url = "https://nowplaying.service.int.example.org/webhook"
    username = "rabe"
    password = "rabe"

    # do work
    send_event(url, username, password)
```

The same event could be sent using cURL:

```bash
cat << EOF > event.json
{
    "specversion": "1.0",
    "type": "ch.rabe.api.events.track.v1.trackStarted",
    "source": "https://github.com/radiorabe/klangbecken",
    "id": "uri:demo:12345",
    "time": "2021-12-28T19:31:00Z",
    "datacontenttype": "application/json",
    "data": {
        "item.title": "Track Title",
        "item.artist": "Artist",
        "item.length": 60
    }
}
EOF
curl -vvv -u rabe:rabe -H 'Content-Type: application/json' -X POST -d '@event.json' \
  https://nowplaying.service.int.example.org/webhook
```

## Contributing

### pre-commit hook

```bash
pip install pre-commit
pip install -r requirements-dev.txt -U
pre-commit install
```

### testing

```bash
pytest
```
