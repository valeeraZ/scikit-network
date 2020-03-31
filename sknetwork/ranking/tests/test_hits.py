#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for hits.py"""

import unittest

from scipy import sparse

from sknetwork.ranking.hits import HITS
from sknetwork.data.test_graphs import *


# noinspection DuplicatedCode,PyMissingOrEmptyDocstring
class TestHITS(unittest.TestCase):

    def test_hits(self):
        hits = HITS()

        adjacency = test_graph()
        n = adjacency.shape[0]
        hits.fit(adjacency)
        self.assertEqual(len(hits.scores_), n)
        self.assertEqual(len(hits.scores_col_), n)

        adjacency = test_digraph()
        n = adjacency.shape[0]
        hits.fit(adjacency)
        self.assertEqual(len(hits.scores_), n)
        self.assertEqual(len(hits.scores_col_), n)

        biadjacency = test_bigraph()
        n1, n2 = biadjacency.shape
        hits.fit(biadjacency)
        self.assertEqual(len(hits.scores_), n1)
        self.assertEqual(len(hits.scores_col_), n2)
