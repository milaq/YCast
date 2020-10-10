import logging
import os

USER_AGENT = 'YCast'
VAR_PATH = os.path.expanduser("~") + '/.ycast'
CACHE_PATH = VAR_PATH + '/cache'


class Directory:
    def __init__(self, name, item_count, displayname=None):
        self.name = name
        self.item_count = item_count
        if displayname:
            self.displayname = displayname
        else:
            self.displayname = name


def generate_stationid_with_prefix(uid, prefix):
    if not prefix or len(prefix) != 2:
        logging.error("Invalid station prefix length (must be 2)")
        return None
    if not uid:
        logging.error("Missing station id for full station id generation")
        return None
    return str(prefix) + '_' + str(uid)


def get_stationid_prefix(uid):
    if len(uid) < 4:
        logging.error("Could not extract stationid (Invalid station id length)")
        return None
    return uid[:2]


def get_stationid_without_prefix(uid):
    if len(uid) < 4:
        logging.error("Could not extract stationid (Invalid station id length)")
        return None
    return uid[3:]


def get_cache_path(cache_name):
    cache_path = CACHE_PATH + '/' + cache_name
    try:
        os.makedirs(cache_path)
    except FileExistsError:
        pass
    except PermissionError:
        logging.error("Could not create cache folders (%s) because of access permissions", cache_path)
        return None
    return cache_path
