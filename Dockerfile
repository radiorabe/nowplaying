FROM ghcr.io/radiorabe/s2i-python:1.1.0 AS build

COPY ./ /opt/app-root/src

RUN python3 setup.py bdist_wheel


FROM ghcr.io/radiorabe/python-minimal:2.0.1 AS app

COPY --from=build /opt/app-root/src/dist/*.whl /tmp/dist/

# update pip first because --use-feature=2020-resolver is now default (and needed so otel doesn't pull protobuf>3)
RUN    python3 -mpip --no-cache-dir install --upgrade pip \
    && python3 -mpip --no-cache-dir install /tmp/dist/*.whl \
    && python3 -mpip --no-cache-dir uninstall --yes pip \
    && rm -rf /tmp/dist/

# make requests use os ca certs that contain the RaBe root CA
ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

USER nobody

CMD ["nowplaying"]
