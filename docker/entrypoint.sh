#!/usr/bin/dumb-init /bin/sh

SCRIPT_DIR=$(dirname $(readlink -f $0))
cd $SCRIPT_DIR

CMD="python3 -m ycast -p $YCAST_PORT -c /etc/stations.yml -d"
echo $CMD
$CMD

