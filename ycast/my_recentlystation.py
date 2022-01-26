import logging
from ycast import generic

MAX_ENTRIES = 15
recently_file = generic.get_var_path() + '/recently.yml'


def signal_station_selected(name, url, icon):
    logging.debug("  %s:%s|%s", name, url, icon)
    list_heard_stations = get_stations_list()
    if len(list_heard_stations) == 0:
        list_heard_stations.append("recently used:\n")
    # make name yaml - like
    name = name.replace(":", " -")

    for line in list_heard_stations:
        elements = line.split(': ')
        if elements[0] == '  '+name:
            list_heard_stations.remove(line)
            logging.debug("Name '%s' exists and deleted", name)
    piped_icon = ''
    if icon and len(icon) > 0:
        piped_icon = '|' + icon

    list_heard_stations.insert(1, '  '+name+': '+url+piped_icon+'\n')
    if len(list_heard_stations) > MAX_ENTRIES+1:
        # remove last (oldest) entry
        list_heard_stations.pop()

    set_stations_yaml(list_heard_stations)


def set_stations_yaml(heard_stations):
    generic.writelns_txt_file(recently_file, heard_stations)


def get_stations_list():
    return generic.readlns_txt_file(recently_file)


def get_recently_stations_yaml():
    return generic.read_yaml_file(recently_file)
