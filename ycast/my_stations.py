import logging
import hashlib

import yaml

import ycast.vtuner as vtuner
import ycast.generic as generic

ID_PREFIX = "MY"

config_file = 'stations.yml'


class Station:
    def __init__(self, uid, name, url, category):
        self.id = generic.generate_stationid_with_prefix(uid, ID_PREFIX)
        self.name = name
        self.url = url
        self.tag = category
        self.icon = None

    def to_vtuner(self):
        return vtuner.Station(self.id, self.name, self.tag, self.url, self.icon, self.tag, None, None, None, None)


def set_config(config):
    global config_file
    if config:
        config_file = config
    if get_stations_yaml():
        return True
    else:
        return False


def get_station_by_id(uid):
    my_stations_yaml = get_stations_yaml()
    if my_stations_yaml:
        for category in my_stations_yaml:
            for station in get_stations_by_category(category):
                if uid == generic.get_stationid_without_prefix(station.id):
                    return station
    return None


def get_stations_yaml():
    try:
        with open(config_file, 'r') as f:
            my_stations = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Station configuration '%s' not found", config_file)
        return None
    except yaml.YAMLError as e:
        logging.error("Station configuration format error: %s", e)
        return None
    return my_stations


def get_category_directories():
    my_stations_yaml = get_stations_yaml()
    categories = []
    if my_stations_yaml:
        for category in my_stations_yaml:
            categories.append(generic.Directory(category, len(get_stations_by_category(category))))
    return categories


def get_stations_by_category(category):
    my_stations_yaml = get_stations_yaml()
    stations = []
    if my_stations_yaml and category in my_stations_yaml:
        for station_name in my_stations_yaml[category]:
            station_url = my_stations_yaml[category][station_name]
            station_id = str(get_checksum(station_name + station_url)).upper()
            stations.append(Station(station_id, station_name, station_url, category))
    return stations


def get_checksum(feed, charlimit=12):
    hash_feed = feed.encode()
    hash_object = hashlib.md5(hash_feed)
    digest = hash_object.digest()
    xor_fold = bytearray(digest[:8])
    for i, b in enumerate(digest[8:]):
        xor_fold[i] ^= b
    digest_xor_fold = ''.join(format(x, '02x') for x in bytes(xor_fold))
    return digest_xor_fold[:charlimit]
