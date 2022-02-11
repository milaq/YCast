FROM alpine:3.15

ARG DOCKER_USER=dockerapp
ARG USER_HOME=/home/$DOCKER_USER
ARG DOCKER_GID=5000
ARG YCAST_PORT=8010

EXPOSE $YCAST_PORT

ENV YCAST_PORT=$YCAST_PORT

RUN adduser -h $USER_HOME -s /bin/sh -u $DOCKER_GID -D $DOCKER_USER

RUN apk update \
    && apk add python3 py3-setuptools dumb-init \
    && apk add --virtual build-tools gcc python3-dev libpq-dev musl-dev \
    && apk add jpeg-dev zlib-dev

ARG SRC_HOME=/usr/local/src
ARG YCAST_SRC=$SRC_HOME/ycast
RUN mkdir -p $YCAST_SRC

COPY ycast/* $YCAST_SRC/
COPY setup.py README.md $SRC_HOME/
COPY examples/stations.yml.example /etc/stations.yml

RUN cd $SRC_HOME && python3 $SRC_HOME/setup.py build && python3 $SRC_HOME/setup.py install

RUN apk del build-tools

COPY docker/entrypoint.sh /usr/local/bin/

WORKDIR $USER_HOME
USER $DOCKER_USER

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh"]
