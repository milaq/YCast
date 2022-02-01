from ycast import generic, my_stations
from ycast.generic import get_recently_file

MAX_ENTRIES = 15
# define a max, so after 5 hits, another station is get better votes
MAX_VOTES = 5
DIRECTORY_NAME = "recently used"

recently_station_dictionary = None
voted5_station_dictinary = None


class StationVote:
    def __init__(self, name, params_txt):
        self.name = name
        params = params_txt.split('|')
        self.url = params[0]
        self.icon = ''
        self.vote = 0
        if len(params) > 1:
            self.icon = params[1]
            if len(params) > 2:
                self.vote = int(params[2])

    def to_params_txt(self):
        text_line = self.url + '|' + self.icon + '|' + str(self.vote)
        return text_line

    def to_server_station(self, cathegory):
        return my_stations.Station(self.name, self.url, cathegory, self.icon)


def signal_station_selected(name, url, icon):
    recently_station_list = get_stations_list()
    station_hit = StationVote(name, url + '|' + icon)
    for recently_station in recently_station_list:
        if name == recently_station.name:
            station_hit.vote = recently_station.vote + 1
            recently_station_list.remove(recently_station)
            break

    recently_station_list.insert(0, station_hit)

    if station_hit.vote > MAX_VOTES:
        for recently_station in recently_station_list:
            if recently_station.vote > 0:
                recently_station.vote = recently_station.vote - 1

    if len(recently_station_list) > MAX_ENTRIES:
        # remove last (oldest) entry
        recently_station_list.pop()

    set_recently_station_dictionary(mk_station_dictionary(directory_name(), recently_station_list))


def set_recently_station_dictionary(station_dict):
    global recently_station_dictionary
    recently_station_dictionary = station_dict
    generic.write_yaml_file(get_recently_file(), recently_station_dictionary)


def mk_station_dictionary(cathegory, station_list):
    new_cathegory_dictionary = {}
    station_dictionary = {}
    for station in station_list:
        station_dictionary[station.name] = station.to_params_txt()

    new_cathegory_dictionary[cathegory] = station_dictionary
    return new_cathegory_dictionary


def get_stations_list():
    stations_list = []
    cathegory_dict = get_recently_stations_dictionary()
    if cathegory_dict:
        for cat_key in cathegory_dict:
            station_dict = cathegory_dict[cat_key]
            for station_key in station_dict:
                stations_list.append(StationVote(station_key, station_dict[station_key]))
    return stations_list


def get_recently_stations_dictionary():
    # cached recently
    global recently_station_dictionary
    if not recently_station_dictionary:
        recently_station_dictionary = generic.read_yaml_file(get_recently_file())
    return recently_station_dictionary


def directory_name():
    station_dictionary = get_recently_stations_dictionary()
    if station_dictionary:
        return list(get_recently_stations_dictionary().keys())[0]
    return DIRECTORY_NAME


# used in landing page
def get_stations_by_vote():
    station_list = get_stations_list()
    station_list.sort(key=lambda station: station.vote, reverse=True)
    station_list = station_list[:5]
    stations = []
    for item in station_list:
        stations.append(item.to_server_station('voted'))
    return stations


def get_stations_by_recently():
    station_list = get_stations_list()
    stations = []
    for item in station_list:
        stations.append(item.to_server_station(directory_name()))
    return stations
