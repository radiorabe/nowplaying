# Dockerfile from s2i --as-dockerfile output, checked in for convenience until we have
# a proper docker registry that can securely be configured.
# Currently hub.docker.io builds are based on this file so it should be updated if the
# s2i base image is updated. In the long run this should get replaced with a toolchain
# that runs docker builds on travis and then pushes them to a registry that allows for
# pushing with an API key or token (like I'm assuming the github registry will allow).
FROM centos/python-36-centos7
LABEL "io.k8s.display-name"="now-playing" \
      "io.openshift.s2i.build.image"="registry.centos.org/centos/python-36-centos7" \
      "io.openshift.s2i.build.source-location"="."

USER root
# Copying in source code
COPY . /tmp/src
# Change file ownership to the assemble user. Builder image must support chown command.
RUN chown -R 1001:0 /tmp/src
USER 1001
# Assemble script sourced from builder image based on user input or image metadata.
# If this file does not exist in the image, the build will fail.
RUN /usr/libexec/s2i/assemble
# Run script sourced from builder image based on user input or image metadata.
# If this file does not exist in the image, the build will fail.
CMD /usr/libexec/s2i/run
