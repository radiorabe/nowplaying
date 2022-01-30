# Radio Bern Now Playing

This repo contains the tool we use to grab, aggregate and publish show, artist and track metadata from various sources.

The nowplaying project grabs info from RaBes playout solution and publishes them to broadcast vectors like DAB+ and Webstreams.

It also takes care of generating our live ticker at songitcker.rabe.ch.

## Overview

The nowplaying daeom takes various sources into account:

- The RABE playout solution (via the [virtual-saemubox](https://github.com/radiorabe/virtual-saemubox) project)
- Input from [Klangbecken](https://github.com/radiorabe/klangbecken)

It then make an informed decision as to what should be our leading PAD data and pushes this to it's track handlers for the following sinks:

- DAB+ (via the [ODR-EncoderManager](https://github.com/Opendigitalradio/ODR-EncoderManager) API)
- Webstream by pushing to out [Icecast](https://icecast.org/) instances

The sources are currently individually implemented and are being replaced with generic [RaBe Cloud Events](https://github.com/radiorabe/event-spec) based sources. In many places the legacy system is underdocumented and this documentation documents the new system.

## Usage

TBD

### RaBe CloudEvents

The nowplaying projects receives httpd [RaBe CloudEvents](https://github.com/radiorabe/event-spec) on a dedicated web service. It reacts to them depending on the event type and source

It supports the following event types:

- `ch.rabe.api.events.track.v1.trackStarted`
- `ch.rabe.api.events.track.v1.trackFinished`

An example `trackStarted` event looks like this:

```json
{
  "specversion": "1.0",
  "type": "ch.rabe.api.events.track.v1.trackStarted",
  "source": "<source>",
  "subject": null,
  "id": "<id>",
  "time": "2021-12-28T19:31:00Z",
  "datacontenttype": "application/json",
  "data": {
    "item.artist": "hairmare fusion sounds collective",
    "item.title": "C L O U D E V E N T W A V E",
    "item.length": 36000
  }
}
```

It can be sent to the nowplaying service using cURL as follows:

```bash
curl -vvv -u rabe:rabe -H 'Content-Type: application/cloudevents+json' -X POST -d '@event.json'  localhost:8080/webhook
```

In most cases the use of a cloudevents-sdk is recommended. The following example is based on the same [python-sdk](https://github.com/cloudevents/sdk-python) nowplaying uses.

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
