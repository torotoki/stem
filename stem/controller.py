#!/usr/bin/python
# -*- coding: utf-8 -*-

import operator, os, pickle, sys
import json
import datetime

import cherrypy
from stem import Stem


class Root:

    exposed = True

    def __init__(self):
        # self.calc = Stem()
        self.calc = Stem(cache='matrix_cache')
        self.calc.add_folder("/works/csisv13/torotoki/data/train_line/json")

        # Following are used for testing stem
        start_time = datetime.time(12, 30)
        A = self.calc.nearest_node(u"渋谷", start_time)
        self.calc.shortest_path(A, u"新宿")
        print "FINISHED"

    def POST(self, hour, minutes, start_station, end_station):
        start_time = datetime.time(int(hour), int(minutes))
        A = self.calc.nearest_node(start_station, start_time)
        (path, all_time) = self.calc.shortest_path(A, end_station)
        result = []
        for node in path:
            output = {'startion': node.station.name,
                      'departure_time': node.departure_time,
                      'arrival_time': node.arrival_time,
                      'line': node.train.line_name,
                      'id': node.id}
            result.append(output)
        path_info = {'time': all_time,
                     'path': result}
        return json.dumps(path_info)

    cherrypy._cp_config = {
        'cherrypy.tools.json_in.on': True
    }



def main():
    # # Some global configuration; note that this could be moved into a
    # # configuration file
    # cherrypy.config.update({
    #     'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
    #     'tools.decode.on': True,
    #     'tools.trailing_slash.on': True,
    #     'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
    # })

    cherrypy.tree.mount(
        Root(), '/api/stem',
        {'/':
         {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )


    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()
