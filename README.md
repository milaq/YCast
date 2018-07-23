# YCast

YCast is a self hosted replacement for the vTuner internet radio service which some Yamaha AVRs use.

It was developed for and tested with the __RX-Vx73__ series.

It _should_ also work for the following Yamaha AVR models:
 * RX-Vx75
 * RX-Vx77
 * RX-Vx79
 * RX-Vx81

YCast is for you if:
 * You do not want to use a proprietary streaming service
 * You are sick of loading and/or downtimes of the vRadio server
 * You are unsure about the vTuner service's future

## Dependencies:
Python version: `3`

Python packages:
 * `PyYAML`
 
## Usage

YCast really does not need much computing power nor bandwidth. It just serves the information to the AVR. The streaming
itself gets handled by the AVR directly, i.e. you can run it on a low-spec RISC machine like a Raspberry Pi.

* Create your initial `stations.yml`. The config follows a basic YAML structure (see below)
* Create a manual entry in your DNS server (read 'Router' for most home users) for:

  `radioyamaha.vtuner.com`

  to point to the local machine running YCast.

* Run `ycast.py` on the target machine.

### Station configuration
```
Category one name:
  First awesome station name: first.awesome/station/URL
  Second awesome station name: second.awesome/station/URL

Category two name:
  Third awesome station name: third.awesome/station/URL
  Fourth awesome station name: fourth.awesome/station/URL
```   

You can also have a look at `stations.yml.example` for how it can be set up.


## Firewall rules

 * The server running YCast does __not__ need internet access
 * The Yamaha AVR needs access to the internet (i.e. to the station URLs you defined)
 * The Yamaha AVR needs to reach port `80` of the machine running YCast

## Web redirects

You can (__and should__) change the `listen_port` and `listen_address` variables in `ycast.py` if you are already running a HTTP server on the target machine
and/or want to proxy or encase YCast access.

It is advised to use a proper webserver (e.g. Nginx) in front of YCast if you can.
Then, you also don't need to run YCast as root and can proxy the requests to YCast running on a higher port (>1024) listening only on `localhost`.

You _need_ to redirect the following URLs from your webserver to YCast (of course listening to requests to `radioyamaha.vtuner.com`):
 * `/setupapp`
 * `/ycast`


## Caveats

YCast was a quick and dirty project to lay the foundation for having a self hosted vTuner emulation.

It is a barebone service at the moment. It provides your AVR with the basic info it needs to play internet radio stations. 
Maybe this will change in the future.
But for now just station names and URLs. No web-based management interface, no coverart, no fancy stuff.

