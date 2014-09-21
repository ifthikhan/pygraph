#!/usr/bin/env python
# encoding: utf-8

from . import logger
from collections import defaultdict, deque, namedtuple
from itertools import ifilterfalse, chain
from . import Edgenode, Graph, WeightedGraph


_default_func = lambda *v: v


class _Traversal(object):

    def __init__(self, graph, start,
                 process_edge=_default_func,
                 process_vert_early=_default_func,
                 process_vert_late=_default_func):
        self.graph = graph
        self.process_vert_early = process_vert_early
        self.process_vert_late = process_vert_late
        self.process_edge = process_edge
        self.discovered = defaultdict(bool)
        self.processed = defaultdict(bool)
        self.discovered[start] = True
        self.start = start
        self.path = defaultdict(lambda: None)

    def filter_discovered(self, adjacents):
        return [adjacent for adjacent in adjacents
                if self.discovered[adjacent] is False]


class bfs(_Traversal):

    def __init__(self, *args, **kwargs):
        _Traversal.__init__(self, graph, start, **kwargs)
        self(self.start)

    def __call__(self, start):
        queue = deque([start])
        while len(queue):
            vertex = queue.popleft()
            self.process_vert_early(vertex)
            self.processed[vertex] = True
            adjacents = self.graph.adjacents(vertex)
            logger.debug("Adjacents of %s => %s", vertex, adjacents)
            for adjacent in adjacents:
                logger.debug("Parent: %s, Adjacent: %s", vertex, adjacent)
                if self.processed[adjacent] is False or self.graph.directed:
                    self.process_edge(vertex, adjacent)
                if self.discovered[adjacent] is False:
                    self.discovered[adjacent] = True
                    self.path[adjacent] = vertex
                    self.process_edge(vertex, adjacent)
                    queue.append(adjacent)
            self.process_vert_late(vertex)


class dfs(_Traversal):

    def __init__(self, *args, **kwargs):
        _Traversal.__init__(self, graph, start, **kwargs)
        self(self.start)

    def __call__(self, vertex):
        self.process_vert_early(vertex)
        adjacents = self.graph.adjacents(vertex)
        logger.debug("Adjacents of %s => %s", vertex, adjacents)
        #adjacents = self.filter_discovered(adjacents)
        #logger.debug("Filtered discovered: %s", adjacents)
        for adjacent in adjacents:
            logger.debug("Parent: %s, Adjacent: %s", vertex, adjacent)
            if self.discovered[adjacent] is False:
                self.discovered[adjacent] = True
                self.path[adjacent] = vertex
                self.process_edge(vertex, adjacent, self)
                self(adjacent)
            elif self.processed[adjacent] is False or self.graph.directed:
                self.process_edge(vertex, adjacent, self)
        self.processed[vertex] = True
        self.process_vert_late(vertex)


