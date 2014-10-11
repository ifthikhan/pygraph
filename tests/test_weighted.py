#!/usr/bin/env python
# encoding: utf-8

import unittest
from pygraph import primms_minimum_spanning_tree
from pygraph import WeightedGraph


class Fixtures(object):

    def create_graph(self, directed=False):
        g = Graph(directed=directed)
        g.insert_edge(1, 2)
        g.insert_edge(2, 3)
        g.insert_edge(3, 4)
        g.insert_edge(4, 5)
        g.insert_edge(5, 1)
        g.insert_edge(1, 6)
        g.insert_edge(2, 5)
        return g

    def create_weighted_graph(self, directed=False):
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


class TestMinimumSpanningTree(unittest.TestCase, Fixtures):

    """Test case docstring."""
    def setUp(self):
        self.min_span_tree = primms_minimum_spanning_tree
        self.g = self.create_weighted_graph()

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
