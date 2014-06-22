#!/usr/bin/env python
# encoding: utf-8

import unittest
import logging
from collections import defaultdict, deque, namedtuple
from itertools import ifilterfalse, chain


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


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


class Graph(object):

    EOL = "\n"

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
            result.append("{} -> {}".format(k, [item.value for item in v]))
        return self.EOL.join(result)


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
        return self.EOL.join(result)


default_func = lambda *v: v


class _Traversal(object):

    def __init__(self, graph, start,
                 process_edge=default_func,
                 process_vert_early=default_func,
                 process_vert_late=default_func):
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


def primms_minimum_spanning_tree(graph, start):
    """Return the minimum spanning tree for the given weighted graph.

    :param graph:
    :type WeightedGraph:
    :param start: An edge of the graph
    :type start: mixed
    """
    assert isinstance(graph, WeightedGraph)
    tree = defaultdict(list)
    tree[start] = []
    while len(tree) < len(graph):
        logger.info("Min Span Tree: %s", dict(tree))
        cheapest_edge_map = {}
        for in_tree_vert in tree:
            adjacents = list(
                ifilterfalse(
                    lambda vert_n_weigt: vert_n_weigt[0] in tree,
                    graph.adjacents(in_tree_vert)))

            logger.debug("Adjacents of in-tree vertex %s: %s", in_tree_vert, adjacents)
            if not adjacents:
                continue

            cheapest_edge_map[in_tree_vert] = min(
                adjacents, key=lambda adjacent_n_weight: adjacent_n_weight[1])
        logger.debug("Least weight edges of all in-tree vertices: %s",
                      cheapest_edge_map)
        in_tree_vert_of_cheapest_edge = min(cheapest_edge_map,
                                            key=lambda k: cheapest_edge_map[k][1])
        vert, weight = cheapest_edge_map[in_tree_vert_of_cheapest_edge]
        logger.info("Cheapest edge: %s, %s", vert, weight)
        tree[in_tree_vert_of_cheapest_edge].append((vert, weight))
        tree[vert] = []
    tree = dict(tree)
    logger.debug("Min span tree: %s", tree)
    return tree


def create_graph(directed=False):
    g = Graph(directed=directed)
    g.insert_edge(1, 2)
    g.insert_edge(2, 3)
    g.insert_edge(3, 4)
    g.insert_edge(4, 5)
    g.insert_edge(5, 1)
    g.insert_edge(1, 6)
    g.insert_edge(2, 5)
    return g


def create_weighted_graph(directed=False):
    g = WeightedGraph(directed=directed)
    g.insert_edge(1, 2, weight=5)
    g.insert_edge(1, 3, weight=7)
    g.insert_edge(1, 4, weight=12)
    g.insert_edge(2, 3, weight=9)
    g.insert_edge(3, 4, weight=4)
    g.insert_edge(2, 5, weight=7)
    g.insert_edge(3, 5, weight=4)
    g.insert_edge(3, 6, weight=3)
    g.insert_edge(4, 6, weight=7)
    g.insert_edge(5, 6, weight=2)
    g.insert_edge(5, 7, weight=5)
    g.insert_edge(6, 7, weight=2)
    return g

class TestMinimumSpanningTree(unittest.TestCase):

    """Test case docstring."""
    def setUp(self):
        self.min_span_tree = primms_minimum_spanning_tree
        self.g = create_weighted_graph()

    def test_none_value_for_graph(self):
        with self.assertRaises(AssertionError):
            self.min_span_tree(None, 1)

    def test_success(self):
        expected_tree = {1: [(2, 5), (3, 7)],
                         2: [],
                         3: [(6, 3), (4, 4)],
                         4: [],
                         5: [],
                         6: [(5, 2), (7, 2)],
                         7: []}
        tree = self.min_span_tree(self.g, 1)
        self.assertEqual(tree, expected_tree)


if __name__ == '__main__':
    unittest.main()



