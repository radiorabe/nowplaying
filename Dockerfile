FROM ghcr.io/radiorabe/python-minimal:0.2.1 AS build

COPY ./ /app/

RUN    cd /app \
    && echo -n "Python Version: " \
    && python -V \
    && microdnf install git-core | tee > /tmp/install.log \
    && python3 -mpip --no-cache-dir install setuptools-git-versioning wheel \
    && python3 setup.py bdist_wheel


FROM ghcr.io/radiorabe/python-minimal:0.2.1 AS app

COPY --from=build /app/dist/*.whl /tmp/dist/

RUN    python3 -mpip --no-cache-dir install /tmp/dist/*.whl \
    && rm -rf /tmp/dist/

# make requests use os ca certs that contain the RaBe root CA
ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

USER nobody

CMD ["nowplaying"]
