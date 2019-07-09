<img src="https://image.ibb.co/iBY6hq/yamaha.png" width="600">

# YCast

YCast is a self hosted replacement for the vTuner internet radio service which many AVRs use.
It emulates a vTuner backend to provide your AVR with the necessary information to play self defined categorized internet radio stations and listen to Radio stations listed in the [Community Radio Browser index](http://www.radio-browser.info).

YCast is for you if:
 * You do not want to use a proprietary streaming service
 * You are sick of loading delays and/or downtimes of the vTuner service
 * You are unsure about the continuation of the vTuner service

## Supported devices

Theoretically, YCast should work for **most AVRs which support vTuner**.

Go ahead and test it with yours, and kindly report the result back :)

### Confirmed working

 * Yamaha RX-Vx73 series (RX-V373, RX-V473, RX-V573, RX-V673, RX-V773)
 * Yamaha R-N500
 * Onkyo TX-NR414
 * Marantz Melody Media M-CR610

### Unconfirmed/Experimental

 * Yamaha RX-Vx75 series (RX-V375, RX-V475, RX-V575, RX-V675, RX-V775)
 * Yamaha RX-Vx77 series (RX-V377, RX-V477, RX-V577, RX-V677, RX-V777)
 * Yamaha RX-Vx79 series (RX-V379, RX-V479, RX-V579, RX-V679, RX-V779)
 * Yamaha RX-Vx81 series (RX-V381, RX-V481, RX-V581, RX-V681, RX-V781)
 * Yamaha RX-S600D
 * Yamaha RX-S601D
 * Yamaha WX-030
 * Yamaha RX-A1060
 * Yamaha RX-V2700
 * Yamaha RX-V3800
 * Yamaha CX-A5000

## Dependencies:
Python version: `3`

Python packages:
 * `flask`
 * `PyYAML`
 
## Usage

YCast really does not need much computing power nor bandwidth. It just serves the information to the AVR. The streaming
itself gets handled by the AVR directly, i.e. you can run it on a low-spec RISC machine like a Raspberry Pi.

You need to create a manual entry in your DNS server (read 'Router' for most home users). `vtuner.com` should point to the machine YCast is running on. Alternatively, in case you only want to forward specific vendors, the following entries may be configured:

  * Yamaha AVRs: `radioyamaha.vtuner.com` (and optionally `radioyamaha2.vtuner.com`)
  * Onkyo AVRs: `onkyo.vtuner.com` (and optionally `onkyo2.vtuner.com`)
  * Denon/Marantz AVRs: `denon.vtuner.com` (and optionally `denon2.vtuner.com`)

If you want to use the 'My Stations' feature besides the global radio index, create a `stations.yml` and run YCast with the `-c` switch to specify the path to it. The config follows a basic YAML structure (see below).

### stations.yml
```
Category one name:
  First awesome station name: first.awesome/station/URL
  Second awesome station name: second.awesome/station/URL

Category two name:
  Third awesome station name: third.awesome/station/URL
  Fourth awesome station name: fourth.awesome/station/URL
```   

### Running

You can run YCast by using the built-in development server of Flask (not recommended for production use, but should(tm) be enough for your private home use): Just run the package: `python -m ycast`

Alternatively you can also setup a proper WSGI server.

 -- TODO: WSGI stuff

You can also have a look at the provided [example](examples/stations.yml.example) to better understand the configuration.


## Web server configuration

While you can simply run YCast with root permissions listening on all interfaces on port 80, this may not be desired for various reasons.

You can change the listen address and port (via `-l` and `-p` respectively) if you are already running a HTTP server on the target machine
and/or want to proxy or restrict YCast access.

It is advised to use a proper webserver (e.g. Nginx) in front of YCast if you can.
Then, you also don't need to run YCast as root and can proxy the requests to YCast running on a higher port (>1024) listening only on `localhost`.

You can redirect all traffic destined for the original request URL (e.g. `radioyamaha.vtuner.com`, `onkyo.vtuner.com`) or need to redirect the following URLs from your webserver to YCast:
 * `/setupapp`
 * `/ycast`

__Attention__: Do not rewrite the request transparently. YCast expects the complete URL (i.e. including `/ycast` or `/setupapp`). It also need an intact `Host` header; so if you're proxying YCast you need to pass the original header on. For Nginx, this can be accomplished with `proxy_set_header Host $host;`.

In case you are using (or plan on using) Nginx to proxy requests, have a look at [this example](examples/nginx-ycast.conf.example).
This can be used together with [this systemd service example](examples/ycast.service.example) for a fully functional deployment.

## Firewall rules

 * The server running YCast does __not__ need internet access.
 * Your AVR needs access to the internet (i.e. to the station URLs you defined).
 * Your AVR needs to reach port `80` of the machine running YCast.

## Caveats

YCast was a quick and dirty project to lay the foundation for having a self hosted vTuner emulation.

It is a barebone service at the moment. It provides your AVR with the basic info it needs to play internet radio stations. 
Maybe this will change in the future, maybe not.
For now just station names and URLs; no web-based management interface, no coverart, no cute kittens, no fancy stuff.
