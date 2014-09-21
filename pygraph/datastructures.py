#!/usr/bin/env python
# encoding: utf-8

"""
Module comprising of all the data structures used by the algorithms.

TODO: Write tests.
"""

from collections import defaultdict


EOL = "\n"


class EdgeNode(object):

    def __init__(self, value, weight=None):
        self.value = value
        self.weight = weight

    def __str__(self):
        return "{self.__class__.__name__}({value=self.value}," \
            " {weight=self.weight})".format(self)

    def __repr__(self):
        return "{self.__class__.__name__}({self.value}," \
            "weight={self.weight})".format(self)

    def __eq__(self, other):
        if self.value == other.value and self.weight == other.weight:
            return True
        return False


class Graph(object):

    def __init__(self, directed=False):
        self.directed = directed
        self.edges = defaultdict(list)

    def insert_edge(self, vertex_start, vertex_end):
        self._insert(vertex_start, EdgeNode(vertex_end))

    def _insert(self, vertex_start, end_edge_node):
        self.edges[vertex_start].append(end_edge_node)
        self.edges[end_edge_node.value]
        if not self.directed:
            self.edges[end_edge_node.value].append(
                EdgeNode(vertex_start, weight=end_edge_node.weight))

    def adjacents(self, vertex):
        return [v.value for v in self.edges[vertex]]

    @property
    def num_edges(self):
        num = 0
        for _, v in self.edges:
            num += len(v)
        return num

    @property
    def num_vertices(self):
        return len(self.edges.keys())

    def degree(self, vertex):
        return len(self.edges[vertex])

    def __len__(self):
        return self.num_vertices

    def __str__(self):
        result = []
        for k, v in self.edges.iteritems():
            result.append("{} -> {}".format(k, [it.value for it in v]))
        return EOL.join(result)


class WeightedGraph(Graph):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    def insert_edge(self, vertex_start, vertex_end, weight):
        self._insert(vertex_start, EdgeNode(vertex_end, weight=weight))

    def adjacents(self, vertex):
        return [(v.value, v.weight) for v in self.edges[vertex]]

    def __str__(self):
        result = []
        for k, v in self.edges.iteritems():
            result.append("{} -> {}".format(
                k, [(item.value, item.weight) for item in v]))
        return EOL.join(result)
