import logging

import yaml

import ycast.vtuner as vtuner
import ycast.generic as generic

ID_PREFIX = "MY"

config_file = 'my_stations.yml'


class Station:
    def __init__(self, name, url, category):
        self.id = generic.generate_stationid_with_prefix('000000', ID_PREFIX)  # TODO: generate meaningful ID
        self.name = name
        self.url = url
        self.tag = category

    def to_vtuner(self):
        return vtuner.Station(self.id, self.name, self.tag, self.url, None, self.tag, None, None, None, None)


def set_config(config):
    global config_file
    if config:
        config_file = config
    if get_stations_yaml():
        return True
    else:
        return False


def get_station_by_id(uid):
    # TODO: return correct station when custom station id generation is implemented, for now just return the very first one for testing
    return get_stations_by_category(get_category_directories()[0].name)[0]


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
            stations.append(Station(station_name, my_stations_yaml[category][station_name], category))
    return stations
