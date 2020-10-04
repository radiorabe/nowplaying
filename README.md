# Radio Bern Now Playing

This repo contains the tool we use to grab, aggregate and publish show, artist and track metadata from various sources.

The nowplaying project grabs info from RaBes playout solution and publishes them to broadcast vectors like DAB+ and Webstreams.

**Warning** The default branch of this repository contains a broken WIP version of nowplaying which is under heavy development.
All current development is happening on the `develop` branch. Currently, no stable version of nowplaying is available.

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
