import base64
import json
import uuid

import requests
import logging

from ycast import __version__, my_filter
import ycast.vtuner as vtuner
import ycast.generic as generic
from ycast.my_filter import check_station, begin_filter, end_filter, get_limit 
from ycast.generic import get_json_attr

API_ENDPOINT = "http://all.api.radio-browser.info"
ID_PREFIX = "RB"

station_cache = {}


class Station:
    def __init__(self, station_json):
        self.stationuuid = generic.get_json_attr(station_json, 'stationuuid')
        self.id = generic.generate_stationid_with_prefix(
            base64.urlsafe_b64encode(uuid.UUID(self.stationuuid).bytes).decode(), ID_PREFIX)
        self.name = generic.get_json_attr(station_json, 'name')

        self.url = generic.get_json_attr(station_json, 'url_resolved')
        if not self.url:
            self.url = generic.get_json_attr(station_json, 'url')

        self.icon = generic.get_json_attr(station_json, 'favicon')
        self.description = generic.get_json_attr(station_json, 'tags')
        self.tags = generic.get_json_attr(station_json, 'tags').split(',')
        self.countrycode = generic.get_json_attr(station_json, 'countrycode')
        self.language = generic.get_json_attr(station_json, 'language')
        self.languagecodes = generic.get_json_attr(station_json, 'languagecodes')
        self.votes = generic.get_json_attr(station_json, 'votes')
        self.codec = generic.get_json_attr(station_json, 'codec')
        self.bitrate = generic.get_json_attr(station_json, 'bitrate')

    def to_vtuner(self):
        return vtuner.Station(self.id, self.name,
                              self.description, self.url, self.icon,
                              self.tags[0], self.countrycode, self.codec, self.bitrate, None)
    def to_dict(self):
        return {'name': self.name , 'url': self.url, 'icon': self.icon, 'description': self.description }

    def get_playable_url(self):
        try:
            playable_url_json = request('url/' + str(self.stationuuid))
            self.url = playable_url_json['url']

        except (IndexError, KeyError):
            logging.error("Could not retrieve first playlist item for station with id '%s'", self.stationuuid)


def request(url):
    logging.debug("Radiobrowser API request: %s", url)
    headers = {'content-type': 'application/json', 'User-Agent': generic.USER_AGENT + '/' + __version__}
    try:
        response = requests.get(API_ENDPOINT + '/json/' + url, headers=headers)
    except requests.exceptions.ConnectionError as err:
        logging.error("Connection to Radiobrowser API failed (%s)", err)
        return {}
    if response.status_code != 200:
        logging.error("Could not fetch data from Radiobrowser API (HTML status %s)", response.status_code)
        return {}
    return response.json()


def get_station_by_id(vtune_id):
    global station_cache
    # decode
    uidbase64 = generic.get_stationid_without_prefix(vtune_id)
    uid = str(uuid.UUID(base64.urlsafe_b64decode(uidbase64).hex()))
    if station_cache:
        station = station_cache[vtune_id]
        if station:
            return station
    # no item in cache, do request
    station_json = request('stations/byuuid?uuids=' + uid)
    if station_json and len(station_json):
        station = Station(station_json[0])
        if station:
            station_cache[station.id] = station
        return station
    return None


def get_country_directories():
    country_directories = []
    apicall = 'countries'
    if not get_limit('SHOW_BROKEN_STATIONS'):
        apicall += '?hidebroken=true'
    countries_raw = request(apicall)
    for country_raw in countries_raw:
        if get_json_attr(country_raw, 'name') and get_json_attr(country_raw, 'stationcount') and \
                int(get_json_attr(country_raw, 'stationcount')) > get_limit('MINIMUM_COUNT_COUNTRY'):
            if my_filter.chk_parameter('country', get_json_attr(country_raw, 'name')):
                country_directories.append(generic.Directory(get_json_attr(country_raw, 'name'),
                                                             get_json_attr(country_raw, 'stationcount')))
    return country_directories


def get_language_directories():
    language_directories = []
    apicall = 'languages'
    if not get_limit('SHOW_BROKEN_STATIONS'):
        apicall += '?hidebroken=true'
    languages_raw = request(apicall)
    for language_raw in languages_raw:
        if get_json_attr(language_raw, 'name') and get_json_attr(language_raw, 'stationcount') and \
                int(get_json_attr(language_raw, 'stationcount')) > get_limit('MINIMUM_COUNT_LANGUAGE'):
            if my_filter.chk_parameter('languagecodes', get_json_attr(language_raw, 'iso_639')):
                language_directories.append(generic.Directory(get_json_attr(language_raw, 'name'),
                                                              get_json_attr(language_raw, 'stationcount'),
                                                              get_json_attr(language_raw, 'name').title()))
    return language_directories


def get_genre_directories():
    genre_directories = []
    apicall = 'tags'
    if not get_limit('SHOW_BROKEN_STATIONS'):
        apicall += '?hidebroken=true'
    genres_raw = request(apicall)
    for genre_raw in genres_raw:
        if get_json_attr(genre_raw, 'name') and get_json_attr(genre_raw, 'stationcount') and \
                int(get_json_attr(genre_raw, 'stationcount')) > get_limit('MINIMUM_COUNT_GENRE'):
            if my_filter.chk_parameter('tags', get_json_attr(genre_raw, 'name')):
                genre_directories.append(generic.Directory(get_json_attr(genre_raw, 'name'),
                                                       get_json_attr(genre_raw, 'stationcount'),
                                                       get_json_attr(genre_raw, 'name').capitalize()))
    return genre_directories


def get_stations_by_country(country):
    begin_filter()
    station_cache.clear()
    stations = []
    stations_list_json = request('stations/search?order=name&reverse=false&countryExact=true&country=' + str(country))
    for station_json in stations_list_json:
        if check_station(station_json):
            cur_station = Station(station_json)
            station_cache[cur_station.id] = cur_station
            stations.append(cur_station)
    end_filter()
    return stations


def get_stations_by_language(language):
    begin_filter()
    station_cache.clear()
    stations = []
    stations_list_json = \
        request('stations/search?order=name&reverse=false&languageExact=true&language=' + str(language))
    for station_json in stations_list_json:
        if check_station(station_json):
            cur_station = Station(station_json)
            station_cache[cur_station.id] = cur_station
            stations.append(cur_station)
    end_filter()
    return stations


def get_stations_by_genre(genre):
    begin_filter()
    station_cache.clear()
    stations = []
    stations_list_json = request('stations/search?order=name&reverse=false&tagExact=true&tag=' + str(genre))
    for station_json in stations_list_json:
        if check_station(station_json):
            cur_station = Station(station_json)
            station_cache[cur_station.id] = cur_station
            stations.append(cur_station)
    end_filter()
    return stations


def get_stations_by_votes(limit=get_limit('DEFAULT_STATION_LIMIT')):
    begin_filter()
    station_cache.clear()
    stations = []
    stations_list_json = request('stations?order=votes&reverse=true&limit=' + str(limit))
    for station_json in stations_list_json:
        if check_station(station_json):
            cur_station = Station(station_json)
            station_cache[cur_station.id] = cur_station
            stations.append(cur_station)
    end_filter()
    return stations


def search(name, limit=get_limit('DEFAULT_STATION_LIMIT')):
    begin_filter()
    station_cache.clear()
    stations = []
    stations_list_json = request('stations/search?order=name&reverse=false&limit=' + str(limit) + '&name=' + str(name))
    for station_json in stations_list_json:
        if check_station(station_json):
            cur_station = Station(station_json)
            station_cache[cur_station.id] = cur_station
            stations.append(cur_station)
    end_filter()
    return stations
