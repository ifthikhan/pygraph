#!/usr/bin/env python
# encoding: utf-8

"""
Module with all the algorithms dealing with weighted graphs.
"""

from collections import defaultdict
from heapq import heapify, heappop, heappush
from . import WeightedGraph


def primms_minimum_spanning_tree(graph, start):
    """Return the minimum spanning tree for the given weighted graph.
    http://en.wikipedia.org/wiki/Prim's_algorithm

    :param graph:
    :type WeightedGraph:
    :param start: An edge of the graph
    :type start: mixed
    """
    assert isinstance(graph, WeightedGraph)
    tree = defaultdict(list)
    tree[start] = []
    heap = []
    last_added_vert = start
    while len(tree) < len(graph):
        logger.info("Last vert added to tree: %s", last_added_vert)
        adjacents = [(weight, vert, last_added_vert) for vert, weight in
                     graph.adjacents(last_added_vert) if vert not in tree]
        logger.debug("Adjacents of in-tree vertex %s: (weight, vert,"
                    " in_tree_vert) %s", last_added_vert, adjacents)
        heap.extend(adjacents)
        heapify(heap)
        logger.info("Verts to choose from: %s", heap)
        weight, vert, in_tree_vert = heappop(heap)
        logger.info("Cheapest edge: %s -> %s, weight: %s", in_tree_vert, vert,
                    weight)
        tree[in_tree_vert].append((vert, weight))
        tree[vert] = []
        last_added_vert = vert
    tree = dict(tree)
    logger.debug("Min span tree: %s", tree)
    return tree
