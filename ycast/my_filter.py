import logging

from ycast import generic
from ycast.generic import get_json_attr

white_list = {'lastcheckok': 1}
black_list = {}
limit_list = {}
limit_defs_int ={ 'MINIMUM_COUNT_GENRE' : 40, 'MINIMUM_COUNT_COUNTRY' : 5, 'MINIMUM_COUNT_LANGUAGE' : 5, 'DEFAULT_STATION_LIMIT' : 200}
limit_defs_bool ={ 'SHOW_BROKEN_STATIONS' : False}
parameter_failed_list = {}
count_used = 0
count_hit = 0

def init_filter_file():
    global white_list, black_list, limit_list
    logging.info('Reading Limits and Filters')
    filter_dictionary = generic.read_yaml_file(generic.get_filter_file())
    if filter_dictionary is None:
        filter_dictionary = {}
        is_updated = True
    if 'whitelist' in filter_dictionary:
        if filter_dictionary['whitelist'] is None:
            white_list = { "lastcheckok" : 1}
        else:
            # Copy so the default is preserved.
            for f in filter_dictionary['whitelist']:
                white_list[f]=filter_dictionary['whitelist'][f]

    if 'blacklist' in filter_dictionary:
        # reference, no defaults
        if filter_dictionary['blacklist'] is None:
            black_list={}
        else:
            black_list=filter_dictionary['blacklist']

    if 'limits' in filter_dictionary:
        set_limits(filter_dictionary['limits'])

def write_filter_config():
    global limit_list
    filter_dictionary = {'whitelist': white_list, 'blacklist': black_list}
    if len(limit_list) > 0: filter_dictionary['limits']=limit_list
    generic.write_yaml_file(generic.get_var_path() + '/filter.yml', filter_dictionary)

def begin_filter():
    global parameter_failed_list
    global count_used
    global count_hit
    count_used = 0
    count_hit = 0

    #init_filter_file()

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
    if isinstance(val, str) and val.find(",") > -1:
        val_list=val.split(",")
    else:
        val_list=[val]
 
    for v in val_list:
        if v == None:
           v='' 
        if isinstance(ref_val, list):
            return v in ref_val
        if str(ref_val) == str(v):
            return True
        if ref_val is None:
            return len(v) == 0
#        if type(val) is int:
##            return val == int(ref_val)
#    if val:
#        return ref_val.find(str(val)) >= 0
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


def get_limit(param_name):
    global limit_defs
    if param_name in limit_defs_int: return limit_list.get(param_name,limit_defs_int[param_name])
    if param_name in limit_defs_bool: return limit_list.get(param_name,limit_defs_bool[param_name])
    else: return None

def get_limit_list():
    global limit_defs_int, limit_defs_bool
    my_limits={}
    limit_defs=dict(limit_defs_int)
    limit_defs.update(limit_defs_bool)
    for l in limit_defs:
         my_limits[l]=get_limit(l)
    return my_limits

def set_limits(limits):
    global limit_list, limit_defs_int, limit_defs_bool
    for l in limits:
        if limits[l] == None:
            limit_list.pop(l, None)
        elif l in limit_defs_int:
            if isinstance(limits[l], int) and limits[l] > 0:
                limit_list[l]=limits[l]
        elif l in limit_defs_bool:
            if isinstance(limits[l], bool): limit_list[l]=limits[l]
        else:
            loggin.error("Invalid limit %s") % l
    return get_limit_list()
