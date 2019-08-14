import logging

import yaml

import ycast.vtuner as vtuner

ID_PREFIX = "MY_"

config_file = 'my_stations.yml'


class Station:
    def __init__(self, name, url, category):
        self.id = ID_PREFIX + '000000'  # TODO: generate meaningful ID
        self.name = name
        self.url = url
        self.tag = category

    def to_vtuner(self):
        return vtuner.Station(self.id, self.name, self.tag, self.url, None, self.tag, None, None, None, None)


def set_config(config):
    global config_file
    if config:
        config_file = config
    if get_stations():
        return True
    else:
        return False


def get_stations():
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


def get_categories():
    my_stations_yaml = get_stations()
    categories = []
    if my_stations_yaml:
        for category in my_stations_yaml:
            categories.append(category)
    return categories


def get_stations_by_category(category):
    my_stations_yaml = get_stations()
    stations = []
    if my_stations_yaml and category in my_stations_yaml:
        for station_name in my_stations_yaml[category]:
            stations.append(Station(station_name, my_stations_yaml[category][station_name], category))
    return stations
