from ycast import generic

MAX_ENTRIES = 15
DIRECTORY_NAME = "recently used"

recently_file = generic.get_var_path() + '/recently.yml'
is_yml_file_loadable = True


def signal_station_selected(name, url, icon):
    list_heard_stations = get_stations_list()
    if not list_heard_stations:
        list_heard_stations = []
        list_heard_stations.append(DIRECTORY_NAME + ":\n")
    # make name yaml - like
    name = name.replace(":", " -")

    for line in list_heard_stations:
        elements = line.split(': ')
        if elements[0] == '  '+name:
            list_heard_stations.remove(line)
    piped_icon = ''
    if icon and len(icon) > 0:
        piped_icon = '|' + icon

    list_heard_stations.insert(1, '  '+name+': '+url+piped_icon+'\n')
    if len(list_heard_stations) > MAX_ENTRIES+1:
        # remove last (oldest) entry
        list_heard_stations.pop()

    set_stations_yaml(list_heard_stations)


def set_stations_yaml(heard_stations):
    global is_yml_file_loadable
    is_yml_file_loadable = generic.writelns_txt_file(recently_file, heard_stations)


def get_stations_list():
    return generic.readlns_txt_file(recently_file)


def get_recently_stations_yaml():
    global is_yml_file_loadable
    dict_stations = None
    if is_yml_file_loadable:
        dict_stations = generic.read_yaml_file(recently_file)
        if not dict_stations:
            is_yml_file_loadable = False
    return dict_stations


def directory_name():
    dir = generic.read_yaml_file(recently_file)
    if dir:
        return list(dir.keys())[0]
    return None
