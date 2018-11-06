<img src="https://image.ibb.co/iBY6hq/yamaha.png" width="600">

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
 * You are sick of loading delays and/or downtimes of the vTuner service
 * You are unsure about the continuation of the service from Yamaha/vTuner

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

### stations.yml
```
Category one name:
  First awesome station name: first.awesome/station/URL
  Second awesome station name: second.awesome/station/URL

Category two name:
  Third awesome station name: third.awesome/station/URL
  Fourth awesome station name: fourth.awesome/station/URL
```   

You can also have a look at the provided [example](examples/stations.yml.example) to better understand the configuration.


## Web server configuration

While you can simply run YCast with root permissions listening on all interfaces on port 80, this may not be desired for various reasons.

You can (and should) change the listen address and port (via `-l` and `-p` respectively) if you are already running a HTTP server on the target machine
and/or want to proxy or restrict YCast access.

It is advised to use a proper webserver (e.g. Nginx) in front of YCast if you can.
Then, you also don't need to run YCast as root and can proxy the requests to YCast running on a higher port (>1024) listening only on `localhost`.

You need to redirect the following URLs from your webserver to YCast (listening to requests to `radioyamaha.vtuner.com`):
 * `/setupapp`
 * `/ycast`

__Attention__: Do not rewrite the request transparently. YCast expects the complete URL (i.e. including `/ycast/`).

In case you are using (or plan on using) Nginx to proxy requests, have a look at [this example](examples/nginx-ycast.conf.example).
This can be used together with [this systemd service example](examples/ycast.service.example) for a fully functional deployment.

## Firewall rules

 * The server running YCast does __not__ need internet access
 * The Yamaha AVR needs access to the internet (i.e. to the station URLs you defined)
 * The Yamaha AVR needs to reach port `80` of the machine running YCast

## Caveats

YCast was a quick and dirty project to lay the foundation for having a self hosted vTuner emulation.

It is a barebone service at the moment. It provides your AVR with the basic info it needs to play internet radio stations. 
Maybe this will change in the future, maybe not.
For now just station names and URLs; no web-based management interface, no coverart, no cute kittens, no fancy stuff.
