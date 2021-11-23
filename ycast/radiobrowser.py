import requests
import logging

from ycast import __version__
import ycast.vtuner as vtuner
import ycast.generic as generic

API_ENDPOINT = "http://all.api.radio-browser.info"
DEFAULT_STATION_LIMIT = 200
SHOW_BROKEN_STATIONS = False
ID_PREFIX = "RB"


def get_json_attr(json, attr):
    try:
        return json[attr]
    except:
        return None


def format_displayname(displayname, apiparam):
    if apiparam == 'languages':
        displayname = displayname.title()
    elif apiparam == 'tags':
        displayname = displayname.capitalize()
    else:
        displayname = None
    return displayname


def request_station_builder(paramtype, param, limit):
    prefix = 'stations/search?order='
    order = 'name&reverse=false'
    lim = '&limit=' + str(limit)
    req = '&' + str(paramtype) + 'Exact=true&' + str(paramtype) + '=' + str(param)
    hidebroken = '&hidebroken=true'
    if SHOW_BROKEN_STATIONS:
        hidebroken = '&hidebroken=false'
    if paramtype == 'votes':
        order = 'votes&reverse=true'
    if paramtype == 'search':
        req = '&name=' + str(param)
    return prefix + order + lim + req + hidebroken


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
    station_json = request('stations/byuuid/' + str(uid))
    if station_json and len(station_json):
        return Station(station_json[0])
    else:
        return None


def get_stations(paramtype, param='', limit=DEFAULT_STATION_LIMIT):
    """
    Generic Function for getting Stations. paramtype must be one
    of search, country, language, tag(getting genres),votes. See
    request_station_builder(paramtype, param, limit) to expand functionality
    """
    stations = []
    stations_json = request(request_station_builder(paramtype, param, limit))
    for station_json in stations_json:
        stations.append(Station(station_json))
    return stations


def get_directories(apiparam, minimumcount=5):
    apicall = apiparam
    directories = []
    if not SHOW_BROKEN_STATIONS:
        apicall += '?hidebroken=true'
    raw_directories = request(apicall)
    for raw_directory in raw_directories:
        if get_json_attr(raw_directory, 'name') and get_json_attr(raw_directory, 'stationcount') and \
                int(get_json_attr(raw_directory, 'stationcount')) > minimumcount:
            directories.append(generic.Directory(get_json_attr(raw_directory, 'name'),
                                                 get_json_attr(raw_directory, 'stationcount'),
                                                 format_displayname(get_json_attr(raw_directory, 'name'), apiparam)))
    return directories
