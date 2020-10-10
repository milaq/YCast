<img src="https://image.ibb.co/iBY6hq/yamaha.png" width="600">

# YCast

[![PyPI latest version](https://img.shields.io/pypi/v/ycast?color=success)](https://pypi.org/project/ycast/) [![GitHub latest version](https://img.shields.io/github/v/release/milaq/YCast?color=success&label=github&sort=semver)](https://github.com/milaq/YCast/releases) [![Python version](https://img.shields.io/pypi/pyversions/ycast)](https://www.python.org/downloads/) [![License](https://img.shields.io/pypi/l/ycast)](https://www.gnu.org/licenses/gpl-3.0.en.html) [![GitHub issues](https://img.shields.io/github/issues/milaq/ycast)](https://github.com/milaq/YCast/issues)

[Get it via PyPI](https://pypi.org/project/ycast/)

[Download from GitHub](https://github.com/milaq/YCast/releases)

[Issue tracker](https://github.com/milaq/YCast/issues)

YCast is a self hosted replacement for the vTuner internet radio service which many AVRs use.
It emulates a vTuner backend to provide your AVR with the necessary information to play self defined categorized internet radio stations and listen to Radio stations listed in the [Community Radio Browser index](http://www.radio-browser.info).

YCast is for you if:
 * You do not want to use a proprietary streaming service
 * You are sick of loading delays and/or downtimes of the vTuner service
 * You do not want to pay for a feature which was free before
 * You are unsure about the continuation of the vTuner service

## Supported devices

Theoretically, YCast should work for **most AVRs which support vTuner**.
Most AVRs with network connectivity that were produced between 2011 and 2017 have vTuner support built-in.

Go ahead, test it with yours and kindly report the results back.
Any reported device helps the community to see which AVRs work properly and which may have issues.

### Confirmed working

 * Denon AVR-X_000 series (AVR-X1000, AVR-2000, AVR-X3000, AVR-X4000)
 * Denon AVR-1912
 * Denon AVR-X2200W
 * Denon CEOL piccolo N5
 * Denon CEOL N9
 * Denon DNP-720AE
 * Denon DNP-730AE
 * Denon DRA-100
 * Marantz Melody Media M-CR610
 * Marantz NR1506
 * Marantz NR1605
 * Marantz NA6005
 * Marantz NA8005
 * Onkyo TX-NR414
 * Onkyo TX-NR5009
 * Onkyo TX-NR616
 * Yamaha R-N301
 * Yamaha R-N500
 * Yamaha RX-A810
 * Yamaha RX-A820
 * Yamaha RX-A830
 * Yamaha CRX-N560/MCR-N560
 * Yamaha RX-V_71 series with network connectivity (RX-V671, RX-V771)
 * Yamaha RX-V_73 series with network connectivity (RX-V473, RX-V573, RX-V673, RX-V773)
 * Yamaha RX-V_75 series (RX-V375, RX-V475, RX-V575, RX-V675, RX-V775)
 * Yamaha RX-V_77 series (RX-V377, RX-V477, RX-V577, RX-V677, RX-V777)
 * Yamaha RX-V3067
 * Yamaha RX-V500D

### Unconfirmed/Experimental

 * Denon AVR-X_100W series (AVR-X1100W, AVR-2100W, AVR-X3100W, AVR-X4100W)
 * Denon AVR-X_300W series (AVR-X1300W, AVR-2300W, AVR-X3300W)
 * Yamaha RX-A1060
 * Yamaha CX-A5000
 * Yamaha RX-S600D
 * Yamaha RX-S601D
 * Yamaha RX-V2700
 * Yamaha RX-V3800
 * Yamaha RX-V_79 series (RX-V379, RX-V479, RX-V579, RX-V679, RX-V779)
 * Yamaha RX-V_81 series (RX-V381, RX-V481, RX-V581, RX-V681, RX-V781)
 * Yamaha WX-030

## Dependencies:
Python version: `3`

Python packages:
 * `requests`
 * `flask`
 * `PyYAML`
 * `Pillow`
 
## Usage

YCast really does not need much computing power nor bandwidth, i.e. you can run it on a low-spec RISC machine like a Raspberry Pi or a home router.

### DNS entries

You need to create a manual entry in your DNS server (read 'Router' for most home users). The `*.vtuner.com` domain should point to the machine YCast is running on.
Specifically the following entries may be configured instead of a wildcard entry:

  * Yamaha AVRs: `radioyamaha.vtuner.com` (and optionally `radioyamaha2.vtuner.com`)
  * Onkyo AVRs: `onkyo.vtuner.com` (and optionally `onkyo2.vtuner.com`)
  * Denon/Marantz AVRs: `denon.vtuner.com` (and optionally `denon2.vtuner.com`)
  * Grundig radios: `grundig.vtuner.com`, `grundig.radiosetup.com` (and optionally `grundig2.vtuner.com` and `grundig2.radiosetup.com`)


### Running the server

#### With built-in webserver

You can run YCast by using the built-in development server of Flask (not recommended for production use, but should™ be enough for your private home use): `python -m ycast`

While you can simply run YCast with root permissions listening on all interfaces on port 80, this may not be desired for various reasons.

You can change the listen address and port (via `-l` and `-p` respectively) if you are already running a HTTP server on the target machine and/or want to proxy or restrict YCast access.

It is advised to use a proper webserver (e.g. Nginx) in front of YCast if you can.
Then, you also don't need to run YCast as root and can proxy the requests to YCast running on a higher port (>1024) listening only on `localhost`.

You can redirect all traffic destined for the original request URL (e.g. `radioyamaha.vtuner.com`, `onkyo.vtuner.com`) or need to redirect the following URLs from your webserver to YCast:
 * `/setupapp`
 * `/ycast`

__Attention__: Do not rewrite the requests transparently. YCast expects the complete URL (i.e. including `/ycast` or `/setupapp`). It also need an intact `Host` header; so if you're proxying YCast you need to pass the original header on. For Nginx, this can be accomplished with `proxy_set_header Host $host;`.

In case you are using (or plan on using) Nginx to proxy requests, have a look at [this example](examples/nginx-ycast.conf.example).
This can be used together with [this systemd service example](examples/ycast.service.example) for a fully functional deployment.

#### With WSGI

You can also setup a proper WSGI server. See the [official Flask documentation](https://flask.palletsprojects.com/en/1.1.x/deploying/).

### Custom stations

If you want to use the 'My Stations' feature, create a `stations.yml` and run YCast with the `-c` switch to specify the path to it. The config follows a basic YAML structure (see below).

```
Category one name:
  First awesome station name: first.awesome/station/URL
  Second awesome station name: second.awesome/station/URL

Category two name:
  Third awesome station name: third.awesome/station/URL
  Fourth awesome station name: fourth.awesome/station/URL
```

You can also have a look at the provided [example](examples/stations.yml.example) to better understand the configuration.

## Firewall rules

 * Your AVR needs access to the internet.
 * Your AVR needs to reach port `80` of the machine running YCast.
 * If you want to use Radiobrowser stations, the machine running YCast needs internet access.

## Caveats

 * vTuner compatible AVRs don't do HTTPS. As such, YCast blindly rewrites every HTTPS station URL to HTTP. Most station
providers which utilize HTTPS for their stations also provide an HTTP stream. Thus, most HTTPS stations should work.
 * The built-in bookmark function does not work at the moment. You need to manually add your favourite stations for now.
