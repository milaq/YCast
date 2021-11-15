import logging
import os
import shutil
import hashlib

USER_AGENT = 'YCast'
VAR_PATH = os.path.expanduser("~") + '/.ycast'
CACHE_PATH = VAR_PATH + '/cache'
CACHE_NAME = 'shortid'


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
    if prefix != 'MY':
        uid = write_uuid(str(uid))
        if not uid:
            logging.error("Unable to store uuid. See previous errors")
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
    wopid = uid[3:]
    if get_stationid_prefix(uid) != 'MY':
        return read_uuid(wopid)
    return wopid


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


def get_checksum(feed, charlimit=12):
    hash_feed = feed.encode()
    hash_object = hashlib.md5(hash_feed)
    digest = hash_object.digest()
    xor_fold = bytearray(digest[:8])
    for i, b in enumerate(digest[8:]):
        xor_fold[i] ^= b
    digest_xor_fold = ''.join(format(x, '02x') for x in bytes(xor_fold))
    return digest_xor_fold[:charlimit]


def write_uuid(uid):
    cache_path = get_cache_path(CACHE_NAME)
    if not cache_path:
        return None
    shortid = get_checksum(uid)
    id_file = cache_path + '/' + shortid
    try:
        with open(id_file, 'w') as file:
            file.write(uid)
    except PermissionError:
        logging.error("Could not access station id file in cache (%s) because of access permissions",
                      id_file)
        return None
    return shortid


def read_uuid(shortid):
    cache_path = get_cache_path(CACHE_NAME)
    if not cache_path:
        return None
    id_file = cache_path + '/' + shortid
    try:
        with open(id_file, 'r') as file:
            uid = file.read()
    except PermissionError:
        logging.error("Could not access station id file in cache (%s) because of access permissions",
                      id_file)
        return None
    return uid


def clear_cache():
    try:
        for root, dirs, files in os.walk(CACHE_PATH):
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
    except OSError:
        logging.error("Could not clean cache)")
