ARG IMAGE
FROM ${IMAGE} as eitri

ARG PRE_COPY_COMMANDS="echo 'Skipping pre-copy commands'"
ARG POST_COPY_COMMANDS="echo 'Skipping post-copy commands'"

RUN ${PRE_COPY_COMMANDS}

COPY . /workplace
WORKDIR /workplace

RUN ${POST_COPY_COMMANDS}