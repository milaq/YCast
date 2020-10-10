import requests
import logging

from ycast import __version__
import ycast.vtuner as vtuner
import ycast.generic as generic

API_ENDPOINT = "http://all.api.radio-browser.info"
MINIMUM_COUNT_GENRE = 5
MINIMUM_COUNT_COUNTRY = 5
MINIMUM_COUNT_LANGUAGE = 5
DEFAULT_STATION_LIMIT = 200
SHOW_BROKEN_STATIONS = False
ID_PREFIX = "RB"


def get_json_attr(json, attr):
    try:
        return json[attr]
    except:
        return None


class Station:
    def __init__(self, station_json):
        self.id = generic.generate_stationid_with_prefix(get_json_attr(station_json, 'stationuuid'), ID_PREFIX)
        self.name = get_json_attr(station_json, 'name')
        self.url = get_json_attr(station_json, 'url')
        self.icon = get_json_attr(station_json, 'favicon')
        self.tags = get_json_attr(station_json, 'tags').split(',')
        self.countrycode = get_json_attr(station_json, 'countrycode')
        self.language = get_json_attr(station_json, 'language')
        self.votes = get_json_attr(station_json, 'votes')
        self.codec = get_json_attr(station_json, 'codec')
        self.bitrate = get_json_attr(station_json, 'bitrate')

    def to_vtuner(self):
        return vtuner.Station(self.id, self.name, ', '.join(self.tags), self.url, self.icon,
                              self.tags[0], self.countrycode, self.codec, self.bitrate, None)

    def get_playable_url(self):
        try:
            playable_url_json = request('url/' + generic.get_stationid_without_prefix(self.id))[0]
            self.url = playable_url_json['url']
        except (IndexError, KeyError):
            logging.error("Could not retrieve first playlist item for station with id '%s'", self.id)


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


def get_station_by_id(uid):
    station_json = request('stations/byid/' + str(uid))
    if station_json and len(station_json):
        return Station(station_json[0])
    else:
        return None


def search(name, limit=DEFAULT_STATION_LIMIT):
    stations = []
    stations_json = request('stations/search?order=name&reverse=false&limit=' + str(limit) + '&name=' + str(name))
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            stations.append(Station(station_json))
    return stations


def get_country_directories():
    country_directories = []
    apicall = 'countries'
    if not SHOW_BROKEN_STATIONS:
        apicall += '?hidebroken=true'
    countries_raw = request(apicall)
    for country_raw in countries_raw:
        if get_json_attr(country_raw, 'name') and get_json_attr(country_raw, 'stationcount') and \
                int(get_json_attr(country_raw, 'stationcount')) > MINIMUM_COUNT_COUNTRY:
            country_directories.append(generic.Directory(get_json_attr(country_raw, 'name'),
                                                         get_json_attr(country_raw, 'stationcount')))
    return country_directories


def get_language_directories():
    language_directories = []
    apicall = 'languages'
    if not SHOW_BROKEN_STATIONS:
        apicall += '?hidebroken=true'
    languages_raw = request(apicall)
    for language_raw in languages_raw:
        if get_json_attr(language_raw, 'name') and get_json_attr(language_raw, 'stationcount') and \
                int(get_json_attr(language_raw, 'stationcount')) > MINIMUM_COUNT_LANGUAGE:
            language_directories.append(generic.Directory(get_json_attr(language_raw, 'name'),
                                                          get_json_attr(language_raw, 'stationcount'),
                                                          get_json_attr(language_raw, 'name').title()))
    return language_directories


def get_genre_directories():
    genre_directories = []
    apicall = 'tags'
    if not SHOW_BROKEN_STATIONS:
        apicall += '?hidebroken=true'
    genres_raw = request(apicall)
    for genre_raw in genres_raw:
        if get_json_attr(genre_raw, 'name') and get_json_attr(genre_raw, 'stationcount') and \
                int(get_json_attr(genre_raw, 'stationcount')) > MINIMUM_COUNT_GENRE:
            genre_directories.append(generic.Directory(get_json_attr(genre_raw, 'name'),
                                                       get_json_attr(genre_raw, 'stationcount'),
                                                       get_json_attr(genre_raw, 'name').capitalize()))
    return genre_directories


def get_stations_by_country(country):
    stations = []
    stations_json = request('stations/search?order=name&reverse=false&countryExact=true&country=' + str(country))
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            stations.append(Station(station_json))
    return stations


def get_stations_by_language(language):
    stations = []
    stations_json = request('stations/search?order=name&reverse=false&languageExact=true&language=' + str(language))
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            stations.append(Station(station_json))
    return stations


def get_stations_by_genre(genre):
    stations = []
    stations_json = request('stations/search?order=name&reverse=false&tagExact=true&tag=' + str(genre))
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            stations.append(Station(station_json))
    return stations


def get_stations_by_votes(limit=DEFAULT_STATION_LIMIT):
    stations = []
    stations_json = request('stations?order=votes&reverse=true&limit=' + str(limit))
    for station_json in stations_json:
        print(station_json)
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            stations.append(Station(station_json))
    return stations
