import logging
import re

import flask
from flask import Flask, request, url_for, redirect, abort, make_response, render_template

import ycast.vtuner as vtuner
import ycast.radiobrowser as radiobrowser
import ycast.my_stations as my_stations
import ycast.generic as generic
import ycast.station_icons as station_icons
import ycast.my_filter as my_filter
from ycast import my_recentlystation
from ycast.my_recentlystation import signal_station_selected

PATH_ROOT = 'ycast'
PATH_PLAY = 'play'
PATH_STATION = 'station'
PATH_SEARCH = 'search'
PATH_ICON = 'icon'
PATH_MY_STATIONS = 'my_stations'
PATH_RADIOBROWSER = 'radiobrowser'
PATH_RADIOBROWSER_COUNTRY = 'country'
PATH_RADIOBROWSER_LANGUAGE = 'language'
PATH_RADIOBROWSER_GENRE = 'genre'
PATH_RADIOBROWSER_POPULAR = 'popular'

station_tracking = False
app = Flask(__name__)


def run(config, address='0.0.0.0', port=8010):
    try:
        generic.set_stations_file(config)
        app.run(host=address, port=port)
    except PermissionError:
        logging.error("No permission to create socket. Are you trying to use ports below 1024 without elevated rights?")


def get_directories_page(subdir, directories, request_obj):
    page = vtuner.Page()
    if len(directories) == 0:
        page.add_item(vtuner.Display("No entries found"))
        page.set_count(1)
        return page
    for directory in get_paged_elements(directories, request_obj.args):
        vtuner_directory = vtuner.Directory(directory.displayname,
                                            url_for(subdir, _external=True, directory=directory.name),
                                            directory.item_count)
        page.add_item(vtuner_directory)
    page.set_count(len(directories))
    return page


def get_stations_page(stations, request_obj):
    page = vtuner.Page()
    page.add_item(vtuner.Previous(url_for('landing', _external=True)))
    if len(stations) == 0:
        page.add_item(vtuner.Display("No stations found"))
        page.set_count(1)
        return page
    for station in get_paged_elements(stations, request_obj.args):
        vtuner_station = station.to_vtuner()
        if station_tracking:
            vtuner_station.set_trackurl(
                request_obj.host_url + PATH_ROOT + '/' + PATH_PLAY + '?id=' + vtuner_station.uid)
        vtuner_station.icon = request_obj.host_url + PATH_ROOT + '/' + PATH_ICON + '?id=' + vtuner_station.uid
        page.add_item(vtuner_station)
    page.set_count(len(stations))
    return page


def get_paged_elements(items, requestargs):
    if requestargs.get('startitems'):
        offset = int(requestargs.get('startitems')) - 1
    elif requestargs.get('startItems'):
        offset = int(requestargs.get('startItems')) - 1
    elif requestargs.get('start'):
        offset = int(requestargs.get('start')) - 1
    else:
        offset = 0
    if offset > len(items):
        logging.warning("Paging offset larger than item count")
        return []
    if requestargs.get('enditems'):
        limit = int(requestargs.get('enditems'))
    elif requestargs.get('endItems'):
        limit = int(requestargs.get('endItems'))
    elif requestargs.get('start') and requestargs.get('howmany'):
        limit = int(requestargs.get('start')) - 1 + int(requestargs.get('howmany'))
    else:
        limit = len(items)
    if limit < offset:
        logging.warning("Paging limit smaller than offset")
        return []
    if limit > len(items):
        limit = len(items)
    return items[offset:limit]


def get_station_by_id(stationid, additional_info=False):
    station_id_prefix = generic.get_stationid_prefix(stationid)
    if station_id_prefix == my_stations.ID_PREFIX:
        return my_stations.get_station_by_id(stationid)
    elif station_id_prefix == radiobrowser.ID_PREFIX:
        station = radiobrowser.get_station_by_id(stationid)
        if additional_info:
            station.get_playable_url()
        return station
    return None


def vtuner_redirect(url):
    if request and request.host and not re.search(r"^[A-Za-z0-9]+\.vtuner\.com$", request.host):
        logging.warning("You are not accessing a YCast redirect with a whitelisted host url (*.vtuner.com). "
                        "Some AVRs have problems with this. The requested host was: %s", request.host)
    return redirect(url, code=302)


@app.route('/setupapp/<path:path>',
           methods=['GET', 'POST'])
def upstream(path):
    logging.debug('upstream **********************')
    if request.args.get('token') == '0':
        return vtuner.get_init_token()
    if request.args.get('search'):
        return station_search()
    if 'statxml.asp' in path and request.args.get('id'):
        return get_station_info()
    if 'navXML.asp' in path:
        return radiobrowser_landing()
    if 'FavXML.asp' in path:
        return my_stations_landing()
    if 'loginXML.asp' in path:
        return landing()
    logging.error("Unhandled upstream query (/setupapp/%s)", path)
    abort(404)

@app.route('/control/filter/<path:item>',
           methods=['POST','GET'])
def set_filters(item):
    update_limits=False
    # POST updates the whitelist or blacklist, GET just returns the current attributes/values.
    myfilter={}
    if item.endswith('blacklist'):
        myfilter=my_filter.black_list
    if item.endswith('whitelist'):
        myfilter=my_filter.white_list
    if item.endswith('limits'):
        myfilter=my_filter.get_limit_list()
        update_limits=True
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.json
        else:
            return  abort(400,'Content-Type not supported!: ' + item)
        if update_limits:
            myfilter=my_filter.set_limits(json)
        else:
            for j in json:
                # Attribute with null value removes item from the list otherwise add the attribute or update the value
                if json[j] == None:
                    myfilter.pop(j, None)
                else:
                    myfilter[j]=json[j]
        my_filter.write_filter_config()
    json=flask.jsonify(myfilter)
    return json

@app.route('/api/<path:path>',
           methods=['GET', 'POST'])
def landing_api(path):
    if request.method == 'GET':
        if path.endswith('stations'):
            category = request.args.get('category')
            stations = None
            if category.endswith('recently'):
                stations = my_recentlystation.get_stations_by_recently()
            if category.endswith('voted'):
                stations = radiobrowser.get_stations_by_votes()
            if category.endswith('language'):
                language = request.args.get('language','german')
                stations = radiobrowser.get_stations_by_language(language)
            if category.endswith('country'):
                country = request.args.get('country','Germany')
                stations = radiobrowser.get_stations_by_country(country)

            if stations is not None:
                stations_dict = []
                for station in stations:
                    stations_dict.append(station.to_dict())

                return flask.jsonify(stations_dict)

        if path.endswith('bookmarks'):
            category = request.args.get('category')
            stations = my_stations.get_all_bookmarks_stations()
            if stations is not None:
                stations_dict = []
                for station in stations:
                    stations_dict.append(station.to_dict())
                return flask.jsonify(stations_dict)

        if path.endswith('paramlist'):
            category = request.args.get('category')
            directories = None
            if category.endswith('language'):
                directories = radiobrowser.get_language_directories();
            if category.endswith('country'):
                directories = radiobrowser.get_country_directories();
            if directories is not None:
                directories_dict = []
                for directory in directories:
                    directories_dict.append(directory.to_dict())
                return flask.jsonify(directories_dict)

    if request.method == 'POST':
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.json
                return flask.jsonify(my_stations.putBookmarkJson(json))
            else:
                return  abort(400,'Content-Type not supported!: ' + path)

    return abort(400,'Not implemented: ' + path)


@app.route('/',
           defaults={'path': ''},
           methods=['GET', 'POST'])
def landing_root(path=''):
    return render_template("index.html")



@app.route('/' + PATH_ROOT + '/',
           defaults={'path': ''},
           methods=['GET', 'POST'])
def landing(path=''):
    logging.debug('===============================================================')
    page = vtuner.Page()

    page.add_item(vtuner.Directory('Radiobrowser', url_for('radiobrowser_landing', _external=True), 4))

    page.add_item(vtuner.Directory('My Stations', url_for('my_stations_landing', _external=True),
                                   len(my_stations.get_category_directories())))

    stations = my_recentlystation.get_stations_by_vote()
    if stations and len(stations) > 0:
        # make blank line (display is not shown)
        page.add_item(vtuner.Spacer())

        for station in stations:
            vtuner_station = station.to_vtuner()
            if station_tracking:
                vtuner_station.set_trackurl(
                    request.host_url + PATH_ROOT + '/' + PATH_PLAY + '?id=' + vtuner_station.uid)
            vtuner_station.icon = request.host_url + PATH_ROOT + '/' + PATH_ICON + '?id=' + vtuner_station.uid
            page.add_item(vtuner_station)

    else:
        page.add_item(vtuner.Display("'My Stations' feature not configured."))
    page.set_count(-1)
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_MY_STATIONS + '/',
           methods=['GET', 'POST'])
def my_stations_landing():
    logging.debug('===============================================================')
    directories = my_stations.get_category_directories()
    return get_directories_page('my_stations_category', directories, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_MY_STATIONS + '/<directory>',
           methods=['GET', 'POST'])
def my_stations_category(directory):
    logging.debug('===============================================================')
    stations = my_stations.get_stations_by_category(directory)
    return get_stations_page(stations, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/',
           methods=['GET', 'POST'])
def radiobrowser_landing():
    logging.debug('===============================================================')
    page = vtuner.Page()
    page.add_item(vtuner.Directory('Genres', url_for('radiobrowser_genres', _external=True),
                                   len(radiobrowser.get_genre_directories())))
    page.add_item(vtuner.Directory('Countries', url_for('radiobrowser_countries', _external=True),
                                   len(radiobrowser.get_country_directories())))
    page.add_item(vtuner.Directory('Languages', url_for('radiobrowser_languages', _external=True),
                                   len(radiobrowser.get_language_directories())))
    page.add_item(vtuner.Directory('Most Popular', url_for('radiobrowser_popular', _external=True),
                                   len(radiobrowser.get_stations_by_votes())))
    page.set_count(4)
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_COUNTRY + '/',
           methods=['GET', 'POST'])
def radiobrowser_countries():
    logging.debug('===============================================================')
    directories = radiobrowser.get_country_directories()
    return get_directories_page('radiobrowser_country_stations', directories, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_COUNTRY + '/<directory>',
           methods=['GET', 'POST'])
def radiobrowser_country_stations(directory):
    logging.debug('===============================================================')
    stations = radiobrowser.get_stations_by_country(directory)
    return get_stations_page(stations, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_LANGUAGE + '/',
           methods=['GET', 'POST'])
def radiobrowser_languages():
    logging.debug('===============================================================')
    directories = radiobrowser.get_language_directories()
    return get_directories_page('radiobrowser_language_stations', directories, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_LANGUAGE + '/<directory>',
           methods=['GET', 'POST'])
def radiobrowser_language_stations(directory):
    logging.debug('===============================================================')
    stations = radiobrowser.get_stations_by_language(directory)
    return get_stations_page(stations, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_GENRE + '/',
           methods=['GET', 'POST'])
def radiobrowser_genres():
    logging.debug('===============================================================')
    directories = radiobrowser.get_genre_directories()
    return get_directories_page('radiobrowser_genre_stations', directories, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_GENRE + '/<directory>',
           methods=['GET', 'POST'])
def radiobrowser_genre_stations(directory):
    logging.debug('===============================================================')
    stations = radiobrowser.get_stations_by_genre(directory)
    return get_stations_page(stations, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_RADIOBROWSER + '/' + PATH_RADIOBROWSER_POPULAR + '/',
           methods=['GET', 'POST'])
def radiobrowser_popular():
    logging.debug('===============================================================')
    stations = radiobrowser.get_stations_by_votes()
    return get_stations_page(stations, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_SEARCH + '/',
           methods=['GET', 'POST'])
def station_search():
    logging.debug('===============================================================')
    query = request.args.get('search')
    if not query or len(query) < 3:
        page = vtuner.Page()
        page.add_item(vtuner.Display("Search query too short"))
        page.set_count(1)
        return page.to_string()
    else:
        # TODO: we also need to include 'my station' elements
        stations = radiobrowser.search(query)
        return get_stations_page(stations, request).to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_PLAY,
           methods=['GET', 'POST'])
def get_stream_url():
    logging.debug('===============================================================')
    stationid = request.args.get('id')
    if not stationid:
        logging.error("Stream URL without station ID requested")
        abort(400)
    station = get_station_by_id(stationid, additional_info=True)
    if not station:
        logging.error("Could not get station with id '%s'", stationid)
        abort(404)
    logging.debug("Station with ID '%s' requested", station.id)
    return vtuner_redirect(station.url)


@app.route('/' + PATH_ROOT + '/' + PATH_STATION,
           methods=['GET', 'POST'])
def get_station_info():
    logging.debug('===============================================================')
    stationid = request.args.get('id')
    if not stationid:
        logging.error("Station info without station ID requested")
        abort(400)
    station = get_station_by_id(stationid, additional_info=(not station_tracking))
    if not station:
        logging.error("Could not get station with id '%s'", stationid)
        page = vtuner.Page()
        page.add_item(vtuner.Display("Station not found"))
        page.set_count(1)
        return page.to_string()
    vtuner_station = station.to_vtuner()
    if station_tracking:
        vtuner_station.set_trackurl(request.host_url + PATH_ROOT + '/' + PATH_PLAY + '?id=' + vtuner_station.uid)
    vtuner_station.icon = request.host_url + PATH_ROOT + '/' + PATH_ICON + '?id=' + vtuner_station.uid
    page = vtuner.Page()
    page.add_item(vtuner_station)
    page.set_count(1)
    return page.to_string()


@app.route('/' + PATH_ROOT + '/' + PATH_ICON,
           methods=['GET', 'POST'])
def get_station_icon():
    logging.debug('**********************:  %s', request.url)
    stationid = request.args.get('id')
    if not stationid:
        logging.error("Station icon without station ID requested")
        abort(400)
    station = get_station_by_id(stationid)
    if not station:
        logging.error("Could not get station with id '%s'", stationid)
        abort(404)
    signal_station_selected(station.name, station.url, station.icon)
    if not hasattr(station, 'icon') or not station.icon:
        logging.warning("No icon information found for station with id '%s'", stationid)
        abort(404)
    station_icon = station_icons.get_icon(station)
    if not station_icon:
        logging.warning("Could not get station icon for station with id '%s'", stationid)
        abort(404)
    response = make_response(station_icon)
    response.headers.set('Content-Type', 'image/jpeg')
    return response
