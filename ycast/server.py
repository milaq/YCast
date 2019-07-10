import logging

import yaml
from flask import Flask, request, url_for

import ycast.vtuner as vtuner
import ycast.radiobrowser as radiobrowser


PATH_ROOT = 'ycast'
PATH_CUSTOM_STATIONS = 'my_stations'
PATH_RADIOBROWSER = 'radiobrowser'
PATH_RADIOBROWSER_COUNTRY = 'country'
PATH_RADIOBROWSER_GENRE = 'genre'
PATH_RADIOBROWSER_POPULAR = 'popular'
PATH_RADIOBROWSER_SEARCH = 'search'

my_stations = {}
app = Flask(__name__)


def run(config, address='0.0.0.0', port=8010):
    try:
        get_stations(config)
        app.run(host=address, port=port)
    except PermissionError:
        logging.error("No permission to create socket. Are you trying to use ports below 1024 without elevated rights?")


def get_stations(config):
    global my_stations
    if not config:
        logging.warning("If you want to use the 'My Stations' feature, please supply a valid station configuration")
        return
    try:
        with open(config, 'r') as f:
            my_stations = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Station configuration '%s' not found", config)
        return
    except yaml.YAMLError as e:
        logging.error("Config error: %s", e)
        return


# TODO: vtuner doesn't do https (e.g. for logos). make an icon cache


@app.route('/', defaults={'path': ''})
@app.route('/setupapp/<path:path>')
@app.route('/' + PATH_ROOT + '/', defaults={'path': ''})
def landing(path):
    if request.args.get('token') == '0':
        return vtuner.get_init_token()
    page = vtuner.Page()
    page.add(vtuner.Directory('Radiobrowser', url_for('radiobrowser_landing', _external=True)))
    page.add(vtuner.Directory('My Stations', url_for('custom_stations_landing', _external=True)))
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_CUSTOM_STATIONS + '/')
def custom_stations_landing():
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for("landing", _external=True)))
    if not my_stations:
        page.add(vtuner.Display("No stations found"))
    else:
        for category in sorted(my_stations, key=str.lower):
            directory = vtuner.Directory(category, url_for('custom_stations_category',
                                                           _external=True, category=category))
            page.add(directory)
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_CUSTOM_STATIONS + '/<category>')
def custom_stations_category(category):
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('custom_stations_landing', _external=True)))
    if category not in my_stations:
        page.add(vtuner.Display("Category '" + category + "' not found"))
    else:
        for station in sorted(my_stations[category], key=str.lower):
            station = vtuner.Station(None, station, None, my_stations[category][station],
                                     None, None, None, None, None, None)
            page.add(station)
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/')
def radiobrowser_landing():
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('landing', _external=True)))
    page.add(vtuner.Directory('Genres', url_for('radiobrowser_genres', _external=True)))
    page.add(vtuner.Directory('Countries', url_for('radiobrowser_countries', _external=True)))
    page.add(vtuner.Directory('Most Popular', url_for('radiobrowser_popular', _external=True)))
    page.add(vtuner.Search('Search', url_for('radiobrowser_search', _external=True, path='')))
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_COUNTRY + '/')
def radiobrowser_countries():
    countries = radiobrowser.get_countries()
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('radiobrowser_landing', _external=True)))
    for country in countries:
        page.add(vtuner.Directory(country, url_for('radiobrowser_country_stations', _external=True, country=country)))
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_COUNTRY + '/<country>')
def radiobrowser_country_stations(country):
    stations = radiobrowser.get_stations_by_country(country)
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('radiobrowser_countries', _external=True)))
    if len(stations) == 0:
        page.add(vtuner.Display("No stations found for country '" + country + "'"))
    else:
        for station in stations:
            page.add(vtuner.Station(station.id, station.name, ', '.join(station.tags), station.url, station.icon,
                                    station.tags[0], station.country, station.codec, station.bitrate, None))
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_GENRE + '/')
def radiobrowser_genres():
    genres = radiobrowser.get_genres()
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('radiobrowser_landing', _external=True)))
    for genre in genres:
        page.add(vtuner.Directory(genre, url_for('radiobrowser_genre_stations', _external=True, genre=genre)))
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_GENRE + '/<genre>')
def radiobrowser_genre_stations(genre):
    stations = radiobrowser.get_stations_by_genre(genre)
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('radiobrowser_genres', _external=True)))
    if len(stations) == 0:
        page.add(vtuner.Display("No stations found for genre '" + genre + "'"))
    else:
        for station in stations:
            page.add(vtuner.Station(station.id, station.name, ', '.join(station.tags), station.url, station.icon,
                                    station.tags[0], station.country, station.codec, station.bitrate, None))
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_POPULAR + '/')
def radiobrowser_popular():
    stations = radiobrowser.get_stations_by_votes()
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('radiobrowser_landing', _external=True)))
    for station in stations:
        page.add(vtuner.Station(station.id, station.name, ', '.join(station.tags), station.url, station.icon,
                                station.tags[0], station.country, station.codec, station.bitrate, None))
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_SEARCH, defaults={'path': ''})
@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_SEARCH + '<path:path>')
def radiobrowser_search(path):
    page = vtuner.Page()
    page.add(vtuner.Previous(url_for('radiobrowser_landing', _external=True)))
    # vtuner does totally weird stuff here: TWO request arguments are passed to the search URI
    # thus, we need to parse the search query as path
    query = None
    if 'search' in path:
        path_search = path[path.find('search'):]
        query = path_search.partition('=')[2]
    if not query or len(query) < 3:
        page.add(vtuner.Display("Search query too short."))
    else:
        stations = radiobrowser.search(query)
        if len(stations) == 0:
            page.add(vtuner.Display("No results for '" + query + "'"))
        else:
            for station in stations:
                page.add(vtuner.Station(station.id, station.name, ', '.join(station.tags), station.url, station.icon,
                                        station.tags[0], station.country, station.codec, station.bitrate, None))
    return page.to_string()
