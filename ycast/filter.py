import logging

from ycast import generic
from ycast.generic import get_json_attr

white_list = {}
black_list = {}
filter_dir = {}
parameter_failed_list = {}


def init_filter():
    global white_list
    global black_list
    global parameter_failed_list
    global filter_dir
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
        logging.info("Used filter parameter: %s", parameter_failed_list)
    else:
        logging.info("Used filter parameter: <nothing used>")


def parameter_hit(param_name):
    count = 1
    old = None
    if parameter_failed_list:
        old = parameter_failed_list.get(param_name)
    if old:
        count = old + 1
    parameter_failed_list[param_name] = count


def check_station(station_json):
    station_name = get_json_attr(station_json, 'name')
    if not station_name:
        # müll response
        logging.debug(station_json)
        return False
# oder verknüpft
    if black_list:
        black_list_hit = False
        for param_name in black_list:
            unvalid_elements = black_list[param_name]
            val = get_json_attr(station_json, param_name)
            if not val == None:
                # attribut in json vorhanden
                if unvalid_elements:
                    if val:
                        pos = unvalid_elements.find(val)
                        black_list_hit = pos >= 0
                else:
                    if not val:
                        black_list_hit = True
                if black_list_hit:
                    parameter_hit(param_name)
#                    logging.debug("FAIL '%s' blacklist hit on '%s' '%s' == '%s'",
#                                  station_name, param_name, unvalid_elements, val)
                    return False

# und verknüpft
    if white_list:
        white_list_hit = True
        for param_name in white_list:
            val = get_json_attr(station_json, param_name)
            if not val == None:
                # attribut in json vorhanden
                valid_elements = white_list[param_name]
                if type(val) is int:
                    white_list_hit = val == valid_elements
                else:
                    if val:
                        pos = valid_elements.find(val)
                        white_list_hit = pos >= 0
                if not white_list_hit:
                    parameter_hit(param_name)
#                    logging.debug("FAIL '%s' whitelist failed on '%s' '%s' == '%s'",
#                                  station_name, param_name, valid_elements, val)
                    return False
#    logging.debug("OK   '%s' passed", station_name)
    return True
