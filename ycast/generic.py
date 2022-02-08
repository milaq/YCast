import logging
import os
import hashlib
import sys

import yaml


USER_AGENT = 'YCast'

# initialize it start
VAR_PATH = ''
CACHE_PATH = ''
stations_file_by_config = ''


class Directory:
    def __init__(self, name, item_count, displayname=None):
        self.name = name
        self.item_count = item_count
        if displayname:
            self.displayname = displayname
        else:
            self.displayname = name

    def to_dict(self):
        return {'name': self.name , 'displayname': self.displayname, 'count': self.item_count }



def mk_writeable_dir(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    except Exception as ex:
        logging.error("Could not create base folder (%s) because of access permissions: %s", path, ex)
        return None
    return path


def init_base_dir(path_element):
    global VAR_PATH, CACHE_PATH
    logging.info('Initialize base directory %s', path_element)
    logging.debug('    HOME: %s',os.path.expanduser("~"))
    logging.debug('     PWD: %s',os.getcwd())
    var_dir = None

    if not os.getcwd().endswith('/ycast'):
        # specified working dir with /ycast has prio
        try_path = os.path.expanduser("~") + path_element
        logging.info('   try Home-Dir: %s', try_path)
        var_dir = mk_writeable_dir(try_path)

    if var_dir is None:
        # avoid using root '/' and it's subdir
        if len(os.getcwd()) < 6:
            logging.error("   len(PWD) < 6 (PWD is too small) < 6: '%s'", os.getcwd())
        else:
            try_path = os.getcwd() + path_element
            logging.info('   try Work-Dir: %s', try_path)
            var_dir = mk_writeable_dir(os.getcwd() + path_element)
        if var_dir is None:
            sys.exit('YCast: ###### No usable directory found #######, I give up....')
    logging.info('using var directory: %s', var_dir)
    VAR_PATH = var_dir
    CACHE_PATH = var_dir + '/cache'
    return


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
    cache_path = CACHE_PATH
    if cache_name:
        cache_path = CACHE_PATH + '/' + cache_name
    try:
        os.makedirs(cache_path)
    except FileExistsError:
        pass
    except PermissionError:
        logging.error("Could not create cache folders (%s) because of access permissions", cache_path)
        return None
    return cache_path


def get_var_path():
    try:
        os.makedirs(VAR_PATH)
    except FileExistsError:
        pass
    except PermissionError:
        logging.error("Could not create cache folders (%s) because of access permissions", VAR_PATH)
        return None
    return VAR_PATH


def get_recently_file():
    return get_var_path() + '/recently.yml'


def get_filter_file():
    return get_var_path() + '/filter.yml'


def get_stations_file():
    global stations_file_by_config
    if stations_file_by_config:
        return stations_file_by_config
    return get_var_path() + '/stations.yml'


def set_stations_file(stations_file):
    global stations_file_by_config
    if stations_file:
        stations_file_by_config = stations_file


def get_checksum(feed, charlimit=12):
    hash_feed = feed.encode()
    hash_object = hashlib.md5(hash_feed)
    digest = hash_object.digest()
    xor_fold = bytearray(digest[:8])
    for i, b in enumerate(digest[8:]):
        xor_fold[i] ^= b
    digest_xor_fold = ''.join(format(x, '02x') for x in bytes(xor_fold))
    return str(digest_xor_fold[:charlimit]).upper()


def read_yaml_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.warning("YAML file '%s' not found", file_name)
    except yaml.YAMLError as e:
        logging.error("YAML format error in '%':\n    %s", file_name, e)
    return None


def write_yaml_file(file_name, dictionary):
    try:
        with open(file_name, 'w') as f:
            # no sort please
            yaml.dump(dictionary, f, sort_keys=False)
            return True
    except yaml.YAMLError as e:
        logging.error("YAML format error in '%':\n    %s", file_name, e)
    except Exception as ex:
        logging.error("File not written '%s':\n    %s", file_name, ex)
    return False


def readlns_txt_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        logging.warning("TXT file '%s' not found", file_name)
    return None


def writelns_txt_file(file_name, line_list):
    try:
        with open(file_name, 'w') as f:
            f.writelines(line_list)
            return True
    except Exception as ex:
        logging.error("File not written '%s':\n    %s", file_name, ex)
    return False


def get_json_attr(json, attr):
    try:
        return json[attr]
    except Exception as ex:
        logging.debug("json: attr '%s' not found: %s", attr, ex)
        return None
