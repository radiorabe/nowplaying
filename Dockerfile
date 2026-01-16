FROM ghcr.io/radiorabe/s2i-python:3.4.3 AS build

COPY ./ /opt/app-root/src

RUN python -mbuild


FROM ghcr.io/radiorabe/python-minimal:3.3.3 AS app

COPY --from=build /opt/app-root/src/dist/*.whl /tmp/dist/

RUN    microdnf install -y \
         python3.12-pip \
    && python -mpip --no-cache-dir install /tmp/dist/*.whl \
    && microdnf remove -y \
         python3.12-pip \
         python3.12-setuptools \
    && microdnf clean all \
    && rm -rf /tmp/dist/ \
    && rm -rf /etc/localtime \
    && ln -s ../usr/share/zoneinfo/Europe/Zurich /etc/localtime

# make requests use os ca certs that contain the RaBe root CA
ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

USER nobody

CMD ["nowplaying"]
