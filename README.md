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
docker run -e APP_SCRIPT=nowplaying/cli.py now-playing:dev
```

The `APP_SCRIPT` argument makes the S2I image call the CLI entrypoint, supplying it will be optional in production.
