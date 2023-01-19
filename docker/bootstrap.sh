#!/bin/sh

#Bootstrap File für ycast docker container
#Variables
#YC_VERSION version of ycast software
#YC_STATIONS path an name of the indiviudual stations.yml e.g. /ycast/stations/stations.yml
#YC_DEBUG turn ON or OFF debug output of ycast server else only start /bin/sh
#YC_PORT port ycast server listens to, e.g. 80

if [ "$YC_DEBUG" = "OFF" ]; then
	/usr/bin/python3 -m ycast -c $YC_STATIONS -p $YC_PORT

elif [ "$YC_DEBUG" = "ON" ]; then
	/usr/bin/python3 -m ycast -c $YC_STATIONS -p $YC_PORT -d

else
	/bin/sh

fi





