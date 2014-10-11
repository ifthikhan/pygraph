#!/usr/bin/env python
# encoding: utf-8

import logging
from collections import defaultdict
from . import bfs, logger


logger = logging.getLogger(__name__)


def find_path(traversed_path, start, end):
    path = []
    def _find(start, end, path):
        if end is None:
            return path
        path.append(end)
        if start == end:
            return path
        else:
            return _find(start, traversed_path[end], path)
    return _find(start, end, path)


def colorize(graph, start, color1="BLACK", color2="WHITE"):
    vertices_color = defaultdict(lambda: None)
    complement = {color1: color2, color2: color1}
    vertices_color[start] = color1

    def process_edge(parent, vertex):
        if vertices_color[parent] == vertices_color[vertex]:
            logger.warning("Not a bipartite graph due %s, %s", parent, vertex)
        vertices_color[vertex] = complement[vertices_color[parent]]
    bfs(graph, start, process_edge=process_edge)
    return dict(vertices_color)


def back_edge_detector(parent, child, traverser):
    """A process edge function to detect back edges."""
    logging.debug("Checking for back edge %s => %s", parent, child)
    is_ancestor = len(find_path(traverser.path, parent, child)) > 0
    if traverser.path[child] != parent  and \
            traverser.path[parent] != child and \
            is_ancestor is True:
        logging.info("Back Edge detected %s => %s", parent, child)


