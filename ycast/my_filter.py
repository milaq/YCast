import logging

from ycast import generic
from ycast.generic import get_json_attr

white_list = {}
black_list = {}
filter_dir = {}
parameter_failed_list = {}
count_used = 0
count_hit = 0


def init_filter():
    global white_list
    global black_list
    global parameter_failed_list
    global filter_dir
    global count_used
    global count_hit
    count_used = 0
    count_hit = 0
    filter_dir = generic.read_yaml_file(generic.get_var_path() + '/filter.yml')
    if filter_dir:
        white_list = filter_dir['whitelist']
        black_list = filter_dir['blacklist']
    else:
        white_list = {'lastcheckok': 1}
        black_list = {}
        filter_dir = {'whitelist': white_list, 'blacklist': black_list}
        generic.write_yaml_file(generic.get_var_path() + '/filter.yml', filter_dir)

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


def chk_paramter(parameter_name, val):
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
                logging.debug("FAIL '%s' blacklist failed on '%s' '%s' == '%s'",
                    station_name, param_name, black_list[param_name], val)
                return False

    # und verknüpft
    if white_list:
        for param_name in white_list:
            val = get_json_attr(station_json, param_name)
            if val is not None:
                # attribut in json vorhanden
                if not verify_value(white_list[param_name], val):
                    parameter_failed_evt(param_name)
                    logging.debug("FAIL '%s' whitelist failed on '%s' '%s' == '%s'",
                                  station_name, param_name, white_list[param_name], val)
                    return False
#    logging.debug("OK   '%s' passed", station_name)
    count_hit = count_hit + 1
    return True
