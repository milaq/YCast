import requests

MINIMUM_COUNT_GENRE = 5
MINIMUM_COUNT_COUNTRY = 5
MINIMUM_BITRATE = 64
STATION_LIMIT_DEFAULT = 99
ID_PREFIX = "RB_"


def get_json_attr(json, attr):
    try:
        return json[attr]
    except:
        return None


class Station:
    def __init__(self, station_json):
        self.id = ID_PREFIX + get_json_attr(station_json, 'id')
        self.name = get_json_attr(station_json, 'name')
        self.url = get_json_attr(station_json, 'url')
        self.icon = get_json_attr(station_json, 'favicon')
        self.tags = get_json_attr(station_json, 'tags').split(',')
        self.country = get_json_attr(station_json, 'country')
        self.language = get_json_attr(station_json, 'language')
        self.votes = get_json_attr(station_json, 'votes')
        self.codec = get_json_attr(station_json, 'codec')
        self.bitrate = get_json_attr(station_json, 'bitrate')


def request(url):
    headers = {'content-type': 'application/json', 'User-Agent': 'YCast'}
    response = requests.get('http://www.radio-browser.info/webservice/json/' + url, headers=headers)
    if response.status_code != 200:
        print("error")
        return None
    return response.json()


def get_station_by_id(uid):
    station_json = request('stations/byid/' + str(uid))
    return Station(station_json[0])


def search(name):
    stations = []
    stations_json = request('stations/search?order=votes&reverse=true&bitrateMin=' +
                            str(MINIMUM_BITRATE) + '&name=' + str(name))
    for station_json in stations_json:
        stations.append(Station(station_json))
    return stations


def get_countries():
    countries = []
    countries_raw = request('countries')
    for country_raw in countries_raw:
        if get_json_attr(country_raw, 'name') and get_json_attr(country_raw, 'stationcount') and \
                int(get_json_attr(country_raw, 'stationcount')) > MINIMUM_COUNT_COUNTRY:
            countries.append(get_json_attr(country_raw, 'name'))
    return countries


def get_genres():
    genres = []
    genres_raw = request('tags?hidebroken=true')
    for genre_raw in genres_raw:
        if get_json_attr(genre_raw, 'name') and get_json_attr(genre_raw, 'stationcount') and \
                int(get_json_attr(genre_raw, 'stationcount')) > MINIMUM_COUNT_GENRE:
            genres.append(get_json_attr(genre_raw, 'name'))
    return genres


def get_stations_by_country(country, limit=STATION_LIMIT_DEFAULT):
    stations = []
    stations_json = request('stations/search?order=votes&reverse=true&bitrateMin=' +
                            str(MINIMUM_BITRATE) + '&limit=' + str(limit) +
                            '&countryExact=true&country=' + str(country))
    for station_json in stations_json:
        stations.append(Station(station_json))
    return stations


def get_stations_by_genre(genre, limit=STATION_LIMIT_DEFAULT):
    stations = []
    stations_json = request('stations/search?order=votes&reverse=true&bitrateMin=' +
                            str(MINIMUM_BITRATE) + '&limit=' + str(limit) + '&tagExact=true&tag=' + str(genre))
    for station_json in stations_json:
        stations.append(Station(station_json))
    return stations


def get_stations_by_votes(limit=STATION_LIMIT_DEFAULT):
    stations = []
    stations_json = request('stations?order=votes&reverse=true&limit=' + str(limit))
    for station_json in stations_json:
        stations.append(Station(station_json))
    return stations
