ARG IMAGE
FROM ${IMAGE} as eitri

ARG PRE_INSTALL="echo 'Skipping pre-copy commands'"
ARG POST_COPY_COMMANDS="echo 'Skipping post-copy commands'"

RUN /bin/bash -c "${PRE_INSTALL}"

COPY . /workspace
WORKDIR /workspace
