import logging

from ycast import generic
from ycast.generic import get_json_attr

white_list = {}
black_list = {}
filter_dictionary = {}
parameter_failed_list = {}
count_used = 0
count_hit = 0

LIMITS_NAME = 'limits'
MINIMUM_COUNT_GENRE = 40
MINIMUM_COUNT_COUNTRY = 5
MINIMUM_COUNT_LANGUAGE = 5
DEFAULT_STATION_LIMIT = 200
SHOW_BROKEN_STATIONS = False


def init_limits_and_filters():
    global MINIMUM_COUNT_GENRE, MINIMUM_COUNT_LANGUAGE, MINIMUM_COUNT_COUNTRY, DEFAULT_STATION_LIMIT, SHOW_BROKEN_STATIONS
    logging.info('Initialize Limits and Filters')
    init_filter_file()
    MINIMUM_COUNT_GENRE = get_limit('MINIMUM_COUNT_GENRE', 40)
    MINIMUM_COUNT_COUNTRY = get_limit('MINIMUM_COUNT_COUNTRY', 5)
    MINIMUM_COUNT_LANGUAGE = get_limit('MINIMUM_COUNT_LANGUAGE', 5)
    DEFAULT_STATION_LIMIT = get_limit('DEFAULT_STATION_LIMIT', 200)
    SHOW_BROKEN_STATIONS = get_limit('SHOW_BROKEN_STATIONS', False)

def init_filter_file():
    global filter_dictionary, white_list, black_list
    filter_dictionary = generic.read_yaml_file(generic.get_filter_file())
    is_updated = False
    if filter_dictionary is None:
        filter_dictionary = {}
        is_updated = True
    if 'whitelist' in filter_dictionary:
        white_list = filter_dictionary['whitelist']
    else:
        white_list = {'lastcheckok': 1}
        is_updated = True

    if 'blacklist' in filter_dictionary:
        black_list = filter_dictionary['blacklist']
    else:
        black_list = {}
        is_updated = True

    if is_updated:
        filter_dictionary = {'whitelist': white_list, 'blacklist': black_list}
        generic.write_yaml_file(generic.get_var_path() + '/filter.yml', filter_dictionary)

def begin_filter():
    global parameter_failed_list
    global count_used
    global count_hit
    count_used = 0
    count_hit = 0

    init_filter_file()

    parameter_failed_list.clear()
    return


def end_filter():
    if parameter_failed_list:
        logging.info("(%d/%d) stations filtered by: %s", count_hit, count_used, parameter_failed_list)
    else:
        logging.info("(%d/%d) stations filtered by: <no filter used>")


def parameter_failed_evt(param_name):
    count = 1
    old = None
    if parameter_failed_list:
        old = parameter_failed_list.get(param_name)
    if old:
        count = old + 1
    parameter_failed_list[param_name] = count


def verify_value(ref_val, val):
    if ref_val == val:
        return True
    if ref_val is None:
        return len(val) == 0
    if type(val) is int:
        return val == int(ref_val)
    if val:
        return ref_val.find(val) >= 0
    return False


def chk_parameter(parameter_name, val):
    if black_list:
        if parameter_name in black_list:
            if verify_value(black_list[parameter_name], val):
                return False
    if white_list:
        if parameter_name in white_list:
            return verify_value(white_list[parameter_name], val)
    return True


def check_station(station_json):
    global count_used
    global count_hit
    count_used = count_used + 1
    station_name = get_json_attr(station_json, 'name')
    if not station_name:
        # müll response
        logging.debug(station_json)
        return False
# oder verknüpft
    if black_list:
        for param_name in black_list:
            val = get_json_attr(station_json, param_name)
            if verify_value(black_list[param_name], val):
                parameter_failed_evt(param_name)
#                logging.debug("FAIL '%s' blacklist failed on '%s' '%s' == '%s'",
#                    station_name, param_name, black_list[param_name], val)
                return False

    # und verknüpft
    if white_list:
        for param_name in white_list:
            val = get_json_attr(station_json, param_name)
            if val is not None:
                # attribut in json vorhanden
                if not verify_value(white_list[param_name], val):
                    parameter_failed_evt(param_name)
#                    logging.debug("FAIL '%s' whitelist failed on '%s' '%s' == '%s'",
#                                  station_name, param_name, white_list[param_name], val)
                    return False
    count_hit = count_hit + 1
    return True


def get_limit(param_name, default):
    global filter_dictionary
    tempdict = generic.read_yaml_file(generic.get_var_path() + '/filter.yml')
    if tempdict is not None:
        filter_dictionary = tempdict
    limits_dict = {}
    if LIMITS_NAME in filter_dictionary:
        limits_dict = filter_dictionary[LIMITS_NAME]
    if param_name in limits_dict:
        return limits_dict[param_name]
    limits_dict[param_name] = default
    filter_dictionary[LIMITS_NAME] = limits_dict
    generic.write_yaml_file(generic.get_var_path() + '/filter.yml', filter_dictionary)
    return default
