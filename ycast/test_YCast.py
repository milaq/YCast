import json
import logging
import os
import unittest
from io import StringIO

import my_filter
import generic
from ycast import radiobrowser, my_recentlystation


class MyTestCase(unittest.TestCase):

    logging.getLogger().setLevel(logging.DEBUG)

    def test_init_filter(self):

        filter.init_filter()

        for elem in filter.filter_dir:
            logging.warning("Name filtertype: %s", elem)
            filter_param = filter.filter_dir[elem]
            if filter_param:
                for par in filter_param:
                    logging.warning("    Name paramter: %s",par)
            else:
                logging.warning("    <empty list>")


    def test_valid_station(self):
        filter.init_filter()
        test_lines = generic.readlns_txt_file(generic.get_var_path()+"/test.json")
        io = StringIO(test_lines[0])
        stations_json = json.load(io)
        count = 0
        for station_json in stations_json:
            if filter.check_station(station_json):
                station = radiobrowser.Station(station_json)
                count = count + 1

        logging.info("Stations (%d/%d)" , count, len(stations_json) )
        logging.info("Used filter parameter", filter.parameter_failed_list)


    def test_popular_station(self):
        stations = radiobrowser.get_stations_by_votes()
        logging.info("Stations (%d)", len(stations))

    def test_recently_hit(self):

        try:
            os.remove(my_recentlystation.recently_file)
        except Exception:
            pass

        result = my_recentlystation.get_stations_by_vote()
        assert len(result) == 0

        result = my_recentlystation.get_recently_stations_dictionary()
        assert result == None

        i = 0
        while i < 10:
            my_recentlystation.signal_station_selected('NAME '+ str(i),'http://dummy/'+ str(i), 'http://icon'+ str(i))
            i = i+1

        result = my_recentlystation.get_recently_stations_dictionary()
        assert my_recentlystation.directory_name()
        assert result[my_recentlystation.directory_name()]

        my_recentlystation.signal_station_selected('Konverenz: Sport' , 'http://dummy/' + str(i), 'http://icon' + str(i))
        my_recentlystation.signal_station_selected('Konverenz: Sport' , 'http://dummy/' + str(i), 'http://icon' + str(i))
        my_recentlystation.signal_station_selected('Konverenz: Sport' , 'http://dummy/' + str(i), 'http://icon' + str(i))

        i = 6
        while i < 17:
            my_recentlystation.signal_station_selected('NAME '+ str(i),'http://dummy/'+ str(i), 'http://icon'+ str(i))
            i = i+1

        result = my_recentlystation.get_recently_stations_dictionary()
        assert result[my_recentlystation.directory_name()]

        result = my_recentlystation.get_stations_by_vote()
        assert len(result) == 5

        j = 0
        while j < 6:
            i = 6
            while i < 9:
                my_recentlystation.signal_station_selected('NAME '+ str(i),'http://dummy/'+ str(i), 'http://icon'+ str(i))
                i = i+1
            j = j+1
        result = my_recentlystation.get_stations_by_vote()
        assert len(result) == 5

if __name__ == '__main__':
    unittest.main()
