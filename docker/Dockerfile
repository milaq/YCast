#
# Docker Buildfile for the ycast-docker container based on alpine linux - about 41.4MB
# put dockerfile and bootstrap.sh in same directory and build or enter
# docker build https://github.com/ThHanika/YCast.git#:docker
#
FROM alpine:latest

#
# Variables
# YC_VERSION version of ycast software
# YC_STATIONS path an name of the indiviudual stations.yml e.g. /ycast/stations/stations.yml
# YC_DEBUG turn ON or OFF debug output of ycast server else only start /bin/sh
# YC_PORT port ycast server listens to, e.g. 80
#
ENV YC_VERSION master
ENV YC_STATIONS /opt/ycast/stations.yml
ENV YC_DEBUG OFF
ENV YC_PORT 80

#
# Upgrade alpine Linux, install python3 and dependencies for pillow - alpine does not use glibc
# pip install needed modules for ycast
#
RUN apk --no-cache update && \
    apk --no-cache upgrade && \
    apk add --no-cache python3 && \
    apk add --no-cache py3-pip && \
    apk add --no-cache zlib-dev && \
    apk add --no-cache jpeg-dev && \
    apk add --no-cache build-base && \
    apk add --no-cache python3-dev && \
    pip3 install --no-cache-dir requests --break-system-packages && \
    pip3 install --no-cache-dir flask --break-system-packages && \
    pip3 install --no-cache-dir PyYAML --break-system-packages && \
    pip3 install --no-cache-dir Pillow  --break-system-packages && \
    pip3 install --no-cache-dir olefile --break-system-packages && \
    mkdir -p /opt/ycast/YCast-master && \
    apk del --no-cache python3-dev && \
    apk del --no-cache build-base && \
    apk del --no-cache zlib-dev && \
    apk add --no-cache curl
# download ycast tar.gz and extract it in ycast Directory
RUN curl -L https://codeload.github.com/superclass/YCast/tar.gz/master \
    | tar xvzC /opt/ycast
# delete unneeded stuff
RUN apk del --no-cache curl && \
    find /usr/lib -name \*.pyc -exec rm -f {} \; && \
    find /usr/lib -type f -name \*.exe -exec rm -f {} \; 

#
# Set Workdirectory on ycast folder
#
WORKDIR /opt/ycast/YCast-${YC_VERSION}

#
# Copy bootstrap.sh to /opt
#
COPY bootstrap.sh /opt

#
# Docker Container should be listening for AVR on port 80
#
EXPOSE ${YC_PORT}/tcp

#
# Start bootstrap on Container start
#
RUN ["chmod", "+x", "/opt/bootstrap.sh"]
ENTRYPOINT ["/opt/bootstrap.sh"]
