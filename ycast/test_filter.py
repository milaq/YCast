import json
import logging
import unittest
from io import StringIO

import filter
import generic
from ycast import radiobrowser

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


if __name__ == '__main__':
    unittest.main()

