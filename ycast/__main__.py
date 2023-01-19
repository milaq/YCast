#!/usr/bin/env python3

import argparse
import logging
import sys
import signal

from ycast import __version__
from ycast import server

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

def handler(signum, frame):
    logging.info('Signal received: rereading filter config')
    from ycast.my_filter import init_filter_file
    init_filter_file()
signal.signal(signal.SIGHUP, handler)

def launch_server():
    parser = argparse.ArgumentParser(description='vTuner API emulation')
    parser.add_argument('-c', action='store', dest='config', help='Station configuration', default=None)
    parser.add_argument('-l', action='store', dest='address', help='Listen address', default='0.0.0.0')
    parser.add_argument('-p', action='store', dest='port', type=int, help='Listen port', default=80)
    parser.add_argument('-d', action='store_true', dest='debug', help='Enable debug logging')
    arguments = parser.parse_args()
    logging.info("YCast (%s) server starting", __version__)
    if arguments.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug logging enabled")
    else:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # initialize important ycast parameters
    from ycast.generic import init_base_dir
    init_base_dir('/.ycast')
    from ycast.my_filter import init_filter_file
    init_filter_file()

    server.run(arguments.config, arguments.address, arguments.port)


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        logging.error("Unsupported Python version (Python %s). Minimum required version is Python 3.",
                      sys.version_info[0])
        sys.exit(1)
    launch_server()
