#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import numpy as np

# class Train:
#     def __init__(self):
#         self.line_name = ""
#         self.joining_line = ""
#         self.provided_company = ""

#         # self.schedule = ""
#         # self.other_info = ""

#         self.train_number = 0
#         self.train_type = ""
#         self.booking_code = ""

class Node:
    def __init__(self):
        pass


class Stem:
    def __init__(self):
        self.nodes = []
        self.vertex = np.array()

    def add_file(self, f_name):
        f = open(f_name)

        train_data = json.load(f)
        f.close()

        train_name = train_data['train_name']
        provided_company = train_data['company'] or ""
        # other_info = train_data['other_info']
        # joining_line = train_data['joining_line']
        # train_number = train_data['train_number']

        for station in train_data['time_table']:
            if station[4] == False:
                print "This station has skip tag"
                continue

            new_node = Node()
            self.nodes.append(new_node)


    def add_folder(self, folder):
        for f_name in os.listdir(folder):
            self.add_file(self, f_name)

    def init(self):
        pass
