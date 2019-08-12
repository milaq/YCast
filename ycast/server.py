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


def get_directories_page(subdir, directories, startitems, enditems):
    page = vtuner.Page()
    if len(directories) == 0:
        page.add(vtuner.Display("No entries found."))
        return page
    offset = 0
    limit = len(directories)
    if startitems and enditems:
        offset = int(startitems) - 1
        limit = int(enditems)
        if offset > len(directories):
            offset = len(directories)
        if limit > len(directories):
            limit = len(directories)
    for directory_num in range(offset, limit):
        directory = directories[directory_num]
        page.add(vtuner.Directory(directory, url_for(subdir, _external=True, directory=directory)))
    return page


def get_stations_page(stations, startitems, enditems):
    page = vtuner.Page()
    if len(stations) == 0:
        page.add(vtuner.Display("No stations found."))
        return page
    offset = 0
    limit = len(stations)
    if startitems and enditems:
        offset = int(startitems) - 1
        limit = int(enditems)
        if offset > len(stations):
            offset = len(stations)
        if limit > len(stations):
            limit = len(stations)
    for station_num in range(offset, limit):
        station = stations[station_num]
        page.add(station.to_vtuner())
    return page


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
    directories = radiobrowser.get_countries()
    return get_directories_page('radiobrowser_country_stations', directories,
                                request.args.get('startitems'), request.args.get('enditems')).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_COUNTRY + '/<directory>')
def radiobrowser_country_stations(directory):
    stations = radiobrowser.get_stations_by_country(directory)
    return get_stations_page(stations, request.args.get('startitems'), request.args.get('enditems')).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_GENRE + '/')
def radiobrowser_genres():
    directories = radiobrowser.get_genres()
    return get_directories_page('radiobrowser_genre_stations', directories,
                                request.args.get('startitems'), request.args.get('enditems')).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_GENRE + '/<directory>')
def radiobrowser_genre_stations(directory):
    stations = radiobrowser.get_stations_by_genre(directory)
    return get_stations_page(stations, request.args.get('startitems'), request.args.get('enditems')).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_POPULAR + '/')
def radiobrowser_popular():
    stations = radiobrowser.get_stations_by_votes()
    return get_stations_page(stations, request.args.get('startitems'), request.args.get('enditems')).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_SEARCH, defaults={'path': ''})
@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_SEARCH + '<path:path>')
def radiobrowser_search(path):
    # vtuner does totally weird stuff here: TWO request arguments are passed to the search URI
    # thus, we need to parse the search query as path
    query = None
    if 'search' in path:
        path_search = path[path.find('search'):]
        query = path_search.partition('=')[2]
    if not query or len(query) < 3:
        page = vtuner.Page()
        page.add(vtuner.Previous(url_for('landing', _external=True)))
        page.add(vtuner.Display("Search query too short."))
        return page.to_string()
    else:
        stations = radiobrowser.search(query)
        return get_stations_page(stations, request.args.get('startitems'), request.args.get('enditems')).to_string()
