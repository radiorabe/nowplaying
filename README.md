# Radio Bern Now Playing

This repo contains the tool we use to grab, aggregate and publish show, artist and track metadata from various sources.

The nowplaying project grabs info from RaBes playout solution and publishes them to broadcast vectors like DAB+ and Webstreams.

It also takes care of generating our live ticker at songticker.rabe.ch.

## Overview

The nowplaying daemon takes various sources into account:

- The RaBe playout solution (via the [virtual-saemubox](https://github.com/radiorabe/virtual-saemubox) project)
- Input from [Klangbecken](https://github.com/radiorabe/klangbecken)

It then make an informed decision as to what should be our leading PAD data and pushes this to it's track handlers for the following sinks:

- DAB+ (via the [ODR-EncoderManager](https://github.com/Opendigitalradio/ODR-EncoderManager) API)
- Webstream by pushing to our [Icecast](https://icecast.org/) instances
- Statically hosted XML output for browsers on songticker.rabe.ch

The sources are currently individually implemented and are being replaced with generic [RaBe CloudEvents](https://github.com/radiorabe/event-spec) based sources. In many places the legacy system is underdocumented and this documentation documents the new system.

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

## Release Management

The CI/CD setup uses semantic commit messages following the [conventional commits standard](https://www.conventionalcommits.org/en/v1.0.0/).
There is a GitHub Action in [.github/workflows/semantic-release.yaml](./.github/workflows/semantic-release.yaml)
that uses [go-semantic-commit](https://go-semantic-release.xyz/) to create new
releases.

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to the consumers of your library:

1. **fix:** a commit of the type `fix` patches gets released with a PATCH version bump
1. **feat:** a commit of the type `feat` gets released as a MINOR version bump
1. **BREAKING CHANGE:** a commit that has a footer `BREAKING CHANGE:` gets released as a MAJOR version bump
1. types other than `fix:` and `feat:` are allowed and don't trigger a release

If a commit does not contain a conventional commit style message you can fix
it during the squash and merge operation on the PR.

Once a commit has landed on the `main` branch a release will be created and automatically published to [pypi](https://pypi.org/)
using the GitHub Action in [.github/workflows/pypi.yaml](./.github/workflows/pypi.yaml) which uses [twine](https://twine.readthedocs.io/)
to publish the package to pypi. Additionaly a container image based on the [RaBe Python Minimal Base Image](https://github.com/radiorabe/container-image-python-minimal) is built and published using [Docker build-push Action](https://github.com/docker/build-push-action).
This is managed in [.github/workflows/release.yaml](./.github/workflows/release.yaml).

## License

This application is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, version 3 of the License.

## Copyright

Copyright (c) 2022 [Radio Bern RaBe](http://www.rabe.ch)
