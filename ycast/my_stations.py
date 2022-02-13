import logging

import ycast.vtuner as vtuner
import ycast.generic as generic

ID_PREFIX = "MY"


class Station:
    def __init__(self, name, url, category, icon):
        self.id = generic.generate_stationid_with_prefix(
            generic.get_checksum(name + url), ID_PREFIX)
        self.name = name
        self.url = url
        self.tag = category
        self.icon = icon

    def to_vtuner(self):
        return vtuner.Station(self.id, self.name, self.tag, self.url, self.icon, self.tag, None, None, None, None)

    def to_dict(self):
        return {'name': self.name , 'url': self.url, 'icon': self.icon, 'description': self.tag }


def get_station_by_id(vtune_id):
    my_stations_yaml = get_stations_yaml()
    if my_stations_yaml:
        for category in my_stations_yaml:
            for station in get_stations_by_category(category):
                if vtune_id == station.id:
                    return station
    return None


def get_stations_yaml():
    from ycast.my_recentlystation import get_recently_stations_dictionary
    my_recently_station = get_recently_stations_dictionary()
    my_stations = generic.read_yaml_file(generic.get_stations_file())
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
            param_list = station_urls.split('|')
            station_url = param_list[0]
            station_icon = None
            if len(param_list) > 1:
                station_icon = param_list[1]
            stations.append(Station(station_name, station_url, category, station_icon))
    return stations

def get_all_bookmarks_stations():
    bm_stations_category = generic.read_yaml_file(generic.get_stations_file())
    stations = []
    if bm_stations_category :
        for category in bm_stations_category:
            for station_name in bm_stations_category[category]:
                station_urls = bm_stations_category[category][station_name]
                param_list = station_urls.split('|')
                station_url = param_list[0]
                station_icon = None
                if len(param_list) > 1:
                    station_icon = param_list[1]
                stations.append(Station(station_name, station_url, category, station_icon))
    return stations


def putBookmarkJson(elements):
    newDict={}
    for stationJson in elements:
        logging.debug("%s ... %s",stationJson['description'], stationJson['name'])
        if stationJson['description'] not in newDict:
            newDict[stationJson['description']] = {}
        logging.debug(stationJson)
        if stationJson['icon'] is not None:
            newDict[stationJson['description']][stationJson['name']] = stationJson['url'] + "|" + stationJson['icon']
        else:
            newDict[stationJson['description']][stationJson['name']] = stationJson['url']

    generic.write_yaml_file(generic.get_stations_file(),newDict)
    return elements
