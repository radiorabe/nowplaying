# Radio Bern Now Playing

This repo contains the tool we use to grab, aggregate and publish show, artist and track metadata from various sources.

The nowplaying project grabs info from RaBes playout solution and publishes them to broadcast vectors like DAB+ and Webstreams.

## Usage

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
