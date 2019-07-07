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

## Building

### Building a Container Image using S2I

You can use the [sclorg S2I Python Container](https://github.com/sclorg/s2i-python-container) to build a container image.

```bash
# Build a FROM centos container image
s2i build --copy . registry.centos.org/centos/python-36-centos7 now-playing:dev

# Build a FROM rhel container image
s2i build --copy . registry.access.redhat.com/rhscl/python-36-rhel7 now-playing:dev
```

The `--copy` flag may be omitted if you are not building a local dev image.

You can run the resulting image using Docker.

```bash
docker run now-playing:dev
```
