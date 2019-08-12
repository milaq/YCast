#!/usr/bin/env python3

import argparse
import logging
import sys

from ycast import server

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


def launch_server():
    parser = argparse.ArgumentParser(description='vTuner API emulation')
    parser.add_argument('-c', action='store', dest='config', help='Station configuration', default=None)
    parser.add_argument('-l', action='store', dest='address', help='Listen address', default='0.0.0.0')
    parser.add_argument('-p', action='store', dest='port', type=int, help='Listen port', default=80)
    arguments = parser.parse_args()
    logging.info("YCast server starting on %s:%s" % (arguments.address, arguments.port))
    server.run(arguments.config, arguments.address, arguments.port)


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        logging.error("Unsupported Python version (Python %s). Minimum required version is Python 3.",
                      sys.version_info[0])
        sys.exit(1)
    launch_server()
