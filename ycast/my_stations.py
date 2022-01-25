import logging
import oyaml as yaml

import ycast.vtuner as vtuner
import ycast.generic as generic

ID_PREFIX = "MY"

config_file = generic.get_var_path() + '/stations.yml'


class Station:
    def __init__(self, uid, name, url, category, icon):
        self.id = generic.generate_stationid_with_prefix(uid, ID_PREFIX)
        self.name = name
        self.url = url
        self.tag = category
        self.icon = icon

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


def get_station_by_id(vtune_id):
    my_stations_yaml = get_stations_yaml()
    if my_stations_yaml:
        for category in my_stations_yaml:
            for station in get_stations_by_category(category):
                if vtune_id == station.id:
                    return station
    return None


def get_stations_yaml():
    from ycast.my_recentlystation import get_recently_stations_yaml
    my_recently_station = get_recently_stations_yaml()
    my_stations = None
    try:
        with open(config_file, 'r') as f:
            my_stations = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Station configuration '%s' not found", config_file)

    except yaml.YAMLError as e:
        logging.error("Station configuration format error: %s", e)

    if my_stations:
        if my_recently_station:
            my_stations.update(my_recently_station)
    else:
        return my_recently_station
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
            station_urls = my_stations_yaml[category][station_name]
            url_list = station_urls.split('|')
            station_url = url_list[0]
            station_icon = None
            if len(url_list) > 1:
                station_icon = url_list[1]
            station_id = generic.get_checksum(station_name + station_url)
            stations.append(Station(station_id, station_name, station_url, category, station_icon))
    return stations
