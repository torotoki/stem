#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO: 乗り換えがうまく扱えていない

import os
import sys
import re
import json
import numpy as np
from scipy import io, sparse
import datetime
import copy
from collections import defaultdict
from heapq import heappush, heappop, heapify
from pdict import priority_dict

MAX_DISTANT = 10000

class Train:
    def __init__(self, id, line_name, provided_company, joining_line):
        self.id = id
        self.line_name = line_name
        self.provided_company = provided_company
        self.joining_line = joining_line

        # self.schedule = ""
        # self.other_info = ""

        self.train_number = 0
        self.train_type = ""
        self.booking_code = ""

class Station:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def get_name(self):
        return self.name

station2node = defaultdict(list)

class Node:
    def __init__(self, id, train, station, departure_time, arrival_time):
        self.id = id
        self.train = train
        self.station = station
        self.departure_time = departure_time
        self.arrival_time = arrival_time


class Stem:
    def __init__(self, cache=None):
        """
        self.nodes は大きさが node 数
        self.vertex は node数 * node数 の行列
        1つのノードは駅名と時間を持っている

        もしくは、self.vertex のみにして、
        edge が 出発駅、出発時間、次の駅、次の駅に着く時間 を
        持つと考えてもこれは可能である。
        こっちのほうがシンプルだが、numpyが使えない。

        MEMO: 本来は出発ノードと着ノードを分けないければ、乗り換えが
        細かい部分で正確に扱えない。
        """

        # If you want to consider mapping station id to that object,
        # name2station should be OrderedDict.
        self.name2station = {}
        self.nodes = []
        self.is_loaded = False
        self.station_nodes = []
        self.station_nodes_buffer = defaultdict(list)
        self.train_nodes_buffer = defaultdict(list)
        self.cache = cache
        # self.vertex = np.array(len(self.nodes), len(self.nodes))

    def time_minus(self, t1, t2):
        # Providing minus operator for 2 times, return minutes of difference of t1 and t2
        dummydate = datetime.date(2000, 1, 1)
        diff = datetime.datetime.combine(dummydate, t1) - datetime.datetime.combine(dummydate, t2)
        return diff.seconds // 60

    def build_vertex(self, train_nodes, station_nodes, nodes):

        # vertex = np.zeros((len(nodes), len(nodes)))
        vertex = sparse.lil_matrix((len(nodes), len(nodes)), dtype=int)

        # Same train nodes
        for i, train in enumerate(train_nodes.values()):
            for j, node in enumerate(train):
                if j == len(train)-1:
                    continue  # last element is skipped
                # if not node.departure_time:
                #     print "node.departure_time is None: %s:%s" % (i, j)
                #     continue
                nnode = train[j+1]
                # vertex[node.id][nnode.id] = nnode.arrival_time - node.departure_time
                if j != 0:
                    diff = self.time_minus(nnode.arrival_time, node.arrival_time)
                else:
                    diff = self.time_minus(nnode.arrival_time, node.departure_time)

                if diff == 0:
                    diff = -1
                vertex[node.id, nnode.id] = diff

        # Same station nodes
        for i, loose_station in enumerate(station_nodes.values()):
            prevs = []
            station = sorted(loose_station, key=lambda x: x.arrival_time or x.departure_time)
            for j, node in enumerate(station):
                # ### ノードが分けられていないため近似計算
                # for prev in prevs[-3:]:
                if prevs:
                    prev = prevs[-1]
                    if not prev.arrival_time:
                        p_arrival_time = prev.departure_time
                    else:
                        p_arrival_time = prev.arrival_time
                    if not node.departure_time:
                        n_departure_time = node.arrival_time
                    else:
                        n_departure_time = node.departure_time
                    if not node.arrival_time:
                        n_arrival_time = node.departure_time
                    else:
                        n_arrival_time = node.arrival_time
                    if not n_departure_time >= p_arrival_time >= n_arrival_time:
                        # To wait in this station
                        diff = self.time_minus(node.arrival_time or node.departure_time,
                                               prev.arrival_time or prev.departure_time)
                        vertex[prev.id, node.id] = diff
                    else:
                        # To exchange to another one in this station
                        vertex[prev.id, node.id] = -1
                        vertex[node.id, prev.id] = -1


                # nnode = station[j+1]
                # # vertex[node.id][nnode.id] = nnode.departure_time - node.arrival_time
                # ### ノードが分けられていないため近似計算

                # if node.arrival_time is None and nnode.arrival_time is None:
                #     diff = self.time_minus(nnode.departure_time, node.departure_time)
                # elif node.arrival_time is None:
                #     # 最初の駅
                #     diff = self.time_minus(nnode.arrival_time, node.departure_time)
                # elif nnode.arrival_time is None:
                #     # 次が終点の駅
                #     diff = self.time_minus(nnode.departure_time, node.arrival_time)

                # else:
                #     # Genneraly case
                #     diff = self.time_minus(nnode.arrival_time, node.arrival_time)

                # if diff == 0:
                #     # not good solution
                #     vertex[node.id, nnode.id] = -1
                #     vertex[nnode.id, node.id] = -1
                # else:
                #     vertex[node.id, nnode.id] = diff
                #     vertex[nnode.id, node.id] = diff
                prevs.append(node)

        return vertex


    def init(self):
        """
        This function is called after loaded all files.
        """
        # self.vertex = np.array(len(self.nodes), len(self.nodes))

        N = len(set(self.name2station.values()))
        MAX_M = max([len(j) for i,j in self.station_nodes_buffer.items()])

        # self.station_nodes = defaultdict(list)
        # for (i, station) in enumerate(self.station_nodes_buffer.keys()):
        #     for (j, node) in enumerate(self.station_nodes_buffer[station]):
        #         # TODO: ここら辺はまだ擬似コード
        #         self.station_nodes[i].append(node)

            #     node.set_id(j)
            # station.set_id(i)

        if self.cache is None:
            self.vertex = self.build_vertex(self.train_nodes_buffer, self.station_nodes_buffer, self.nodes)
            io.savemat('matrix_cache', {'vertex':self.vertex})
            print "made cache file, you should use it"
        else:
            self.vertex = io.loadmat(self.cache)['vertex']

        self.vertex = self.vertex.tocsr()

        # Initializing instant variables for discriminative memory
        # self.train_nodes_buffer = None
        # self.station_nodes_buffer = None

        self.is_loaded = True

        print "nodes: %s" % len(self.nodes)
        print "stations: %s" % N
        print "station and node: %s * %s" % (N, MAX_M)
        print "vertex: %s * %s" % (len(self.nodes), len(self.nodes))
        # print self.vertex

    def _to_station(self, name):
        # TODO: If same name stations, following code cannot convert
        # the names to proper objects
        exists = self.name2station.get(name)
        if exists:
            return exists
        else:
            # Make new station object
            new_id = len(self.name2station)
            new_station = Station(name, new_id)
            self.name2station[name] = new_station
            return new_station

    def decode_time(self, raw_time):
        if raw_time != "":
            (hour, minute) = raw_time.split(':')
            return datetime.time(int(hour), int(minute), 0)
        else:
            return None

    def overlup(self, lis):
        r = []
        def func(x, y):
            if x == y and x not in r:
                r.append(x)
            return y
        reduce(func, lis)
        return r


    def add_file(self, f_name):
        f = open(f_name)

        train_data = json.load(f)
        f.close()

        new_id = len(self.train_nodes_buffer.keys())
        train_name = train_data['train_name']
        provided_company = train_data['company'] or ""
        # other_info = train_data['other_info']
        joining_line = train_data['joining_line']
        train = Train(new_id, train_name, provided_company, joining_line)

        prev_node = None
        for node_info in train_data['time_table']:
            if node_info[3] == True:
                # print "This station has skip tag"
                continue

            station_name = node_info[0]
            raw_arrival_time = node_info[1]
            raw_departure_time = node_info[2]

            # station = Station(station_name)
            station = self._to_station(station_name)
            departure_time = self.decode_time(raw_departure_time)
            arrival_time = self.decode_time(raw_arrival_time)

            new_id = len(self.nodes)  # ID for each node
            for i in (set(self.train_nodes_buffer[train]) &
                      set(self.station_nodes_buffer[station])):
                if i.departure_time == departure_time and i.arrival_time == arrival_time:
                    already_contained_flag = True
                    # existed_node =
                    break
            else:
                already_contained_flag = False

            if not already_contained_flag:
                new_node = Node(new_id, train, station, departure_time, arrival_time)
                self.station_nodes_buffer[station].append(new_node)
                self.train_nodes_buffer[train].append(new_node)
                self.nodes.append(new_node)
                # self.vertex.append([0, 0, 0, ..., from, 0])


    def add_folder(self, folder, then_init=True):
        for f_name in os.listdir(folder):
            self.add_file(folder +'/'+ f_name)
        if then_init:
            self.init()

    def nearest_node(self, station_name, time):
        if not self.is_loaded:
            raise "Please init before calling this function"

        station = self._to_station(station_name)
        nearest_node = None
        nearest_diff = 1000
        for node in self.station_nodes_buffer[station]:
            if node.departure_time:
                diff = self.time_minus(node.departure_time, time)
            else:
                diff = self.time_minus(node.arrival_time, time)

            if diff < nearest_diff and diff >= 0:
                nearest_node = node
        return nearest_node

    def shortest_path(self, start_node, end_station_name):
        if not self.is_loaded:
            raise "Please init before calling this function"

        end_station = self._to_station(end_station_name)

        # # Making a heap queue
        # print "初期化"
        # prev = [-1]*len(self.nodes)
        # dist = [MAX_DISTANT]*len(self.nodes)
        # dist[start_node.id] = 0
        # # Q is a priority queue version of 'dist'
        # Q = priority_dict({i:v for i,v in enumerate(dist)})

        # ###

        # dist = [MAX_DISTANT]*len(self.name2station)
        # dist[start_node.station.id] = 0

        # print "ループ"
        # while Q:
        #     u = Q.pop_smallest()  # argmin node
        #     if u == MAX_DISTANT:
        #         print "u is MAX_DISTANT"

        #     for v in np.nonzero(self.vertex[u])[1]:
        #         length_uv = self.vertex[u, v]
        #         if length_uv == -1:  # using it instead of 0
        #             length_uv = 0

        #         alt = dist[self.nodes[u].station.id] + length_uv
        #         if alt < dist[self.nodes[v].station.id]:
        #             print self.nodes[v].station.name, self.nodes[v].departure_time, self.nodes[v].arrival_time, self.nodes[v].train.line_name, alt
        #             dist[self.nodes[v].station.id] = alt
        #             prev[v] = u
        #             Q[v] = alt

        #             if self.nodes[v].station.name == end_station_name:
        #                 return prev
        # else:
        #     print "全探索したが見つからない"
        #     return prev


        # Making a heap queue
        print "初期化"
        prev = [-1]*len(self.nodes)
        dist = [MAX_DISTANT]*len(self.nodes)
        dist[start_node.id] = 0
        # Q is a priority queue version of 'dist'
        Q = priority_dict({i:v for i,v in enumerate(dist)})

        ###
        # N = len(self.name2station)
        # M = len(self.train_nodes_buffer)
        # dist = np.zeros((N, M, 2), dtype=int)

        # dist = [MAX_DISTANT]*len(self.name2station)
        # dist[start_node.station.id] = 0

        print "ループ"
        while Q:
            u = Q.pop_smallest()  # argmin node
            if u == MAX_DISTANT:
                print "u is MAX_DISTANT"

            for v in np.nonzero(self.vertex[u])[1]:
                raw_length_uv = self.vertex[u, v]
                if raw_length_uv == -1:  # using it instead of 0
                    length_uv = 0
                else:
                    length_uv = raw_length_uv

                alt = dist[u] + length_uv
                if alt < dist[v]:
                    print v, self.nodes[v].station.name, self.nodes[v].arrival_time, self.nodes[v].departure_time, self.nodes[v].train.line_name, alt, len(np.nonzero(self.vertex[u])[1])
                    if self.nodes[v].station.name == u"武蔵小杉":
                        pass
                    dist[v] = alt
                    prev[v] = u
                    Q[v] = alt

                    if self.nodes[v].station.name == end_station_name:
                        return prev
        else:
            print "全探索したが見つからない"
            return prev
