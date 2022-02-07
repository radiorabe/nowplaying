FROM ghcr.io/radiorabe/python-minimal:0.2.1

COPY ./ /app/

RUN    cd /app \
    && microdnf install git-core | tee > /tmp/install.log \
    && python3 -mpip --no-cache-dir install setuptools-git-versioning \
    && python3 -mpip --no-cache-dir install . \
    && microdnf remove `awk '/^Installing: [a-zA-Z]+/ {print $2}' /tmp/install.log | awk -F ';' '{printf $1 " "}'` \
    && microdnf clean all \
    && rm -rf /app/ /tmp/install.log

# make requests use os ca certs that contain the RaBe root CA
ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem

USER nobody

CMD ["nowplaying"]
