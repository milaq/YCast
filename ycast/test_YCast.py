import json
import logging
import os
import unittest
from io import StringIO

import flask

from ycast import my_filter, generic, radiobrowser, my_recentlystation


class MyTestCase(unittest.TestCase):

    logging.getLogger().setLevel(logging.DEBUG)
    generic.init_base_dir("/.test_ycast")
    my_filter.init_filter_file()


    def test_verify_values(self):
        assert my_filter.verify_value(None, None)
        assert my_filter.verify_value('', '')
        assert my_filter.verify_value(None, '')
        assert my_filter.verify_value(3, 3)
        assert my_filter.verify_value('3', 3)
        assert my_filter.verify_value('3', '3')
        assert my_filter.verify_value('3,4,5,6', '5')

        assert not my_filter.verify_value('', None)
        assert not my_filter.verify_value('', '3')
        assert not my_filter.verify_value(3, 4)
        assert not my_filter.verify_value('3', 4)
        assert not my_filter.verify_value('4', '3')
        assert not my_filter.verify_value('3,4,5,6', '9')

    def test_init_filter(self):
        my_filter.begin_filter()
        filter_dictionary={ "whitelist" : my_filter.white_list, "blacklist" : my_filter.black_list}
        for elem in filter_dictionary:
            logging.warning("Name filtertype: %s", elem)
            filter_param = filter_dictionary[elem]
            if filter_param:
                for par in filter_param:
                    logging.warning("    Name paramter: %s", par)
            else:
                logging.warning("    <empty list>")

    def test_life_popular_station(self):
        # hard test for filter
        stations = radiobrowser.get_stations_by_votes(10000000)
        logging.info("Stations (%d)", len(stations))

    def test_get_languages(self):
        result = radiobrowser.get_language_directories()
        logging.info("Languages (%d)", len(result))
        # Based on the example filter is should yield 2
        assert len(result) == 2

    def test_get_countries(self):
        my_filter.init_filter_file()

        result = radiobrowser.get_country_directories()
        logging.info("Countries (%d)", len(result))
        # Test for Germany only 1, nach der Wiedervereinigung...
        assert len(result) == 1

    def test_get_genre(self):
        result = radiobrowser.get_genre_directories()
        logging.info("Genres (%d)", len(result))
        # Not a useful test, changes all the time
        #assert len(result) < 300

    def test_get_limits(self):
        result = my_filter.get_limit('MINIMUM_COUNT_COUNTRY')
        assert result == 5
        result = my_filter.get_limit('SHOW_BROKEN_STATIONS')
        assert result == False

    def test_recently_hit(self):

        try:
            os.remove(my_recentlystation.get_recently_file())
        except Exception:
            pass

        result = my_recentlystation.get_stations_by_vote()
        assert len(result) == 0

        result = my_recentlystation.get_recently_stations_dictionary()
        assert result is None

        i = 0
        while i < 10:
            my_recentlystation.signal_station_selected('NAME ' + str(i), 'http://dummy/' + str(i),
                                                       'http://icon' + str(i))
            i = i+1

        result = my_recentlystation.get_recently_stations_dictionary()
        assert my_recentlystation.directory_name()
        assert result[my_recentlystation.directory_name()]

        my_recentlystation.signal_station_selected('Konverenz: Sport', 'http://dummy/' + str(i),
                                                   'http://icon' + str(i))
        my_recentlystation.signal_station_selected('Konverenz: Sport', 'http://dummy/' + str(i),
                                                   'http://icon' + str(i))
        my_recentlystation.signal_station_selected('Konverenz: Sport', 'http://dummy/' + str(i),
                                                   'http://icon' + str(i))

        i = 6
        while i < 17:
            my_recentlystation.signal_station_selected('NAME ' + str(i), 'http://dummy/' + str(i),
                                                       'http://icon' + str(i))
            i = i+1

        result = my_recentlystation.get_recently_stations_dictionary()
        assert result[my_recentlystation.directory_name()]

        result = my_recentlystation.get_stations_by_vote()
        assert len(result) == 5

        j = 0
        while j < 6:
            i = 6
            while i < 9:
                my_recentlystation.signal_station_selected('NAME ' + str(i), 'http://dummy/' + str(i),
                                                           'http://icon' + str(i))
                i = i+1
            j = j+1
        result = my_recentlystation.get_stations_by_vote()
        assert len(result) == 5


if __name__ == '__main__':
    unittest.main()
