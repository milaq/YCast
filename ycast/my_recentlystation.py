import logging
import os

import yaml

VAR_PATH = os.path.expanduser("~") + '/.ycast'
MAX_ENTRIES = 15

config_file = VAR_PATH + '/recently.yml'


def signal_station_selected(name, url, icon):
    logging.debug("  %s:%s|%s", name, url, icon)
    list_heared_stations = get_stations_list()
    if len(list_heared_stations) == 0:
        list_heared_stations.append("recently used:\n")
    # make name yaml - like
    name = name.replace(":", " -")

    for line in list_heared_stations:
        elements = line.split(': ')
        if elements[0] == '  '+name:
            list_heared_stations.remove(line)
            logging.debug("Name '%s' exists and deleted", name)
    piped_icon = ''
    if icon and len(icon) > 0:
        piped_icon = '|' + icon

    list_heared_stations.insert(1, '  '+name+': '+url+piped_icon+'\n')
    if len(list_heared_stations) > MAX_ENTRIES+1:
        # remove last (oldest) entry
        list_heared_stations.pop()

    set_stations_yaml(list_heared_stations)


def set_stations_yaml(heared_stations):
    try:
        os.makedirs(VAR_PATH)
    except FileExistsError:
        pass
    except PermissionError:
        logging.error("Could not create folders (%s) because of access permissions", VAR_PATH)
        return None

    try:
        with open(config_file, 'w') as f:
            f.writelines(heared_stations)
            logging.info("File written '%s'", config_file)

    except Exception as ex:
        logging.error("File not written '%s': %s", config_file, ex)


def get_stations_list():
    try:
        with open(config_file, 'r') as f:
            heared_stations = f.readlines()
    except FileNotFoundError:
        logging.warning("File not found '%s' not found", config_file)
        return []
    except yaml.YAMLError as e:
        logging.error("Station configuration format error: %s", e)
        return []
    return heared_stations


def get_recently_stations_yaml():
    try:
        with open(config_file, 'r') as f:
            my_stations = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Station configuration '%s' not found", config_file)
        return None
    except yaml.YAMLError as e:
        logging.error("Station configuration format error: %s", e)
        return None
    return my_stations
