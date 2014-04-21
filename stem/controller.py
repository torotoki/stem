#!/usr/bin/python
# -*- coding: utf-8 -*-

import operator, os, pickle, sys

import cherrypy
from stem import Stem

class Root(object):

    def __init__(self, data):
        self.data = data
        # self.calc = Stem()
        self.calc = Stem(cache='matrix_cache')
        self.calc.add_folder("/works/csisv13/torotoki/data/train_line/json")

        # Following are used for testing stem
        import datetime
        start_time = datetime.time(12, 30)
        A = self.calc.nearest_node(u"自由が丘", start_time)
        print self.calc.shortest_path(A, u"渋谷")

    @cherrypy.expose
    def index(self):
        return 'Geddit'


def main():
    data = {} # We'll replace this later

    # Some global configuration; note that this could be moved into a
    # configuration file
    cherrypy.config.update({
        'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
        'tools.decode.on': True,
        'tools.trailing_slash.on': True,
        'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
    })

    cherrypy.quickstart(Root(data), '/', {
        '/media': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    })

if __name__ == '__main__':
    main()
