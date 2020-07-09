#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May, 2020
@author: Nathan de Lara <ndelara@enst.fr>
"""
from abc import ABC
from typing import Union, Iterable

import numpy as np
from scipy import sparse

from sknetwork.linkpred.base import BaseLinkPred
from sknetwork.linkpred.first_order_core import c_common_neigh, c_jaccard, c_salton, c_sorensen, c_hub_promoted,\
    c_hub_depressed, adamic_adar, resource_allocation
from sknetwork.utils.check import check_format


class FirstOrder(BaseLinkPred, ABC):
    """Base class for first order algorithms."""
    def __init__(self):
        super(FirstOrder, self).__init__()
        self.indptr_ = None
        self.indices_ = None

    def fit(self, adjacency: Union[sparse.csr_matrix, np.ndarray]):
        """Fit algorithm to the data.

        Parameters
        ----------
        adjacency :
            Adjacency matrix of the graph

        Returns
        -------
        self : :class:`FirstOrder`
        """
        adjacency = check_format(adjacency)
        adjacency.sort_indices()
        self.indptr_ = adjacency.indptr.astype(np.int32)
        self.indices_ = adjacency.indices.astype(np.int32)

        return self

    def _predict_node(self, source: int):
        """Prediction for a single edge."""
        n = self.indptr_.shape[0] - 1
        return self._predict_base(source, np.arange(n))


class CommonNeighbors(FirstOrder):
    """Link prediction by common neighbors:

    :math:`s(i, j) = |\\Gamma_i \\cap \\Gamma_j|`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> cn = CommonNeighbors()
    >>> similarities = cn.fit_predict(adjacency, 0)
    >>> similarities
    array([2, 1, 1, 1, 1])
    >>> similarities = cn.predict([0, 1])
    >>> similarities
    array([[2, 1, 1, 1, 1],
           [1, 3, 0, 2, 1]])
    >>> similarities = cn.predict((0, 1))
    >>> similarities
    1
    >>> similarities = cn.predict([(0, 1), (1, 2)])
    >>> similarities
    array([1, 0])
    """
    def __init__(self):
        super(CommonNeighbors, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(c_common_neigh(self.indptr_, self.indices_, np.int32(source),
                                         np.array(targets, dtype=np.int32))).astype(int)


class JaccardIndex(FirstOrder):
    """Link prediction by Jaccard Index:

    :math:`s(i, j) = \\dfrac{|\\Gamma_i \\cap \\Gamma_j|}{|\\Gamma_i \\cup \\Gamma_j|}`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> jaccard = JaccardIndex()
    >>> similarities = jaccard.fit_predict(adjacency, 0)
    >>> similarities.round(2)
    array([1.  , 0.25, 0.33, 0.33, 0.25])
    >>> similarities = jaccard.predict([0, 1])
    >>> similarities.round(2)
    array([[1.  , 0.25, 0.33, 0.33, 0.25],
           [0.25, 1.  , 0.  , 0.67, 0.2 ]])
    >>> similarities = jaccard.predict((0, 1))
    >>> similarities.round(2)
    0.25
    >>> similarities = jaccard.predict([(0, 1), (1, 2)])
    >>> similarities.round(2)
    array([0.25, 0.  ])

    References
    ----------
    Jaccard, P. (1901) étude comparative de la distribution florale dans une portion des Alpes et du Jura.
    Bulletin de la Société Vaudoise des Sciences Naturelles, 37, 547-579.
    """
    def __init__(self):
        super(JaccardIndex, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(c_jaccard(self.indptr_, self.indices_, np.int32(source), np.array(targets, dtype=np.int32)))


class SaltonIndex(FirstOrder):
    """Link prediction by Salton Index:

    :math:`s(i, j) = \\dfrac{|\\Gamma_i \\cap \\Gamma_j|}{\\sqrt{|\\Gamma_i|.|\\Gamma_j|}}`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> salton = SaltonIndex()
    >>> similarities = salton.fit_predict(adjacency, 0)
    >>> similarities.round(2)
    array([1.  , 0.41, 0.5 , 0.5 , 0.41])
    >>> similarities = salton.predict([0, 1])
    >>> similarities.round(2)
    array([[1.  , 0.41, 0.5 , 0.5 , 0.41],
           [0.41, 1.  , 0.  , 0.82, 0.33]])
    >>> similarities = salton.predict((0, 1))
    >>> similarities.round(2)
    0.41
    >>> similarities = salton.predict([(0, 1), (1, 2)])
    >>> similarities.round(2)
    array([0.41, 0.  ])

    References
    ----------
    Martínez, V., Berzal, F., & Cubero, J. C. (2016).
    `A survey of link prediction in complex networks.
    <https://dl.acm.org/doi/pdf/10.1145/3012704>`_
    ACM computing surveys (CSUR), 49(4), 1-33.
    """
    def __init__(self):
        super(SaltonIndex, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(c_salton(self.indptr_, self.indices_, np.int32(source), np.array(targets, dtype=np.int32)))


class SorensenIndex(FirstOrder):
    """Link prediction by Salton Index:

    :math:`s(i, j) = \\dfrac{2|\\Gamma_i \\cap \\Gamma_j|}{|\\Gamma_i|+|\\Gamma_j|}`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> sorensen = SorensenIndex()
    >>> similarities = sorensen.fit_predict(adjacency, 0)
    >>> similarities.round(2)
    array([1. , 0.4, 0.5, 0.5, 0.4])
    >>> similarities = sorensen.predict([0, 1])
    >>> similarities.round(2)
    array([[1.  , 0.4 , 0.5 , 0.5 , 0.4 ],
           [0.4 , 1.  , 0.  , 0.8 , 0.33]])
    >>> similarities = sorensen.predict((0, 1))
    >>> similarities.round(2)
    0.4
    >>> similarities = sorensen.predict([(0, 1), (1, 2)])
    >>> similarities.round(2)
    array([0.4, 0. ])

    References
    ----------
    Martínez, V., Berzal, F., & Cubero, J. C. (2016).
    `A survey of link prediction in complex networks.
    <https://dl.acm.org/doi/pdf/10.1145/3012704>`_
    ACM computing surveys (CSUR), 49(4), 1-33.
    """
    def __init__(self):
        super(SorensenIndex, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(c_sorensen(self.indptr_, self.indices_, np.int32(source), np.array(targets, dtype=np.int32)))


class HubPromotedIndex(FirstOrder):
    """Link prediction by Hub Promoted Index:

    :math:`s(i, j) = \\dfrac{2|\\Gamma_i \\cap \\Gamma_j|}{min(|\\Gamma_i|,|\\Gamma_j|)}`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> hpi = HubPromotedIndex()
    >>> similarities = hpi.fit_predict(adjacency, 0)
    >>> similarities.round(2)
    array([1. , 0.5, 0.5, 0.5, 0.5])
    >>> similarities = hpi.predict([0, 1])
    >>> similarities.round(2)
    array([[1.  , 0.5 , 0.5 , 0.5 , 0.5 ],
           [0.5 , 1.  , 0.  , 1.  , 0.33]])
    >>> similarities = hpi.predict((0, 1))
    >>> similarities.round(2)
    0.5
    >>> similarities = hpi.predict([(0, 1), (1, 2)])
    >>> similarities.round(2)
    array([0.5, 0. ])

    References
    ----------
    Martínez, V., Berzal, F., & Cubero, J. C. (2016).
    `A survey of link prediction in complex networks.
    <https://dl.acm.org/doi/pdf/10.1145/3012704>`_
    ACM computing surveys (CSUR), 49(4), 1-33.
    """
    def __init__(self):
        super(HubPromotedIndex, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(c_hub_promoted(self.indptr_, self.indices_, np.int32(source),
                                         np.array(targets, dtype=np.int32)))


class HubDepressedIndex(FirstOrder):
    """Link prediction by Hub Depressed Index:

    :math:`s(i, j) = \\dfrac{2|\\Gamma_i \\cap \\Gamma_j|}{max(|\\Gamma_i|,|\\Gamma_j|)}`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> hdi = HubDepressedIndex()
    >>> similarities = hdi.fit_predict(adjacency, 0)
    >>> similarities.round(2)
    array([1.  , 0.33, 0.5 , 0.5 , 0.33])
    >>> similarities = hdi.predict([0, 1])
    >>> similarities.round(2)
    array([[1.  , 0.33, 0.5 , 0.5 , 0.33],
           [0.33, 1.  , 0.  , 0.67, 0.33]])
    >>> similarities = hdi.predict((0, 1))
    >>> similarities.round(2)
    0.33
    >>> similarities = hdi.predict([(0, 1), (1, 2)])
    >>> similarities.round(2)
    array([0.33, 0.  ])

    References
    ----------
    Martínez, V., Berzal, F., & Cubero, J. C. (2016).
    `A survey of link prediction in complex networks.
    <https://dl.acm.org/doi/pdf/10.1145/3012704>`_
    ACM computing surveys (CSUR), 49(4), 1-33.
    """
    def __init__(self):
        super(HubDepressedIndex, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(c_hub_depressed(self.indptr_, self.indices_, np.int32(source),
                                          np.array(targets, dtype=np.int32)))


class AdamicAdar(FirstOrder):
    """Link prediction by Adamic-Adar index:

    :math:`s(i, j) = \\underset{z \\in \\Gamma_i \\cap \\Gamma_j}{\\sum} \\dfrac{1}{\\log |\\Gamma_z|}`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> aa = AdamicAdar()
    >>> similarities = aa.fit_predict(adjacency, 0)
    >>> similarities.round(2)
    array([1.82, 0.91, 0.91, 0.91, 0.91])
    >>> similarities = aa.predict([0, 1])
    >>> similarities.round(2)
    array([[1.82, 0.91, 0.91, 0.91, 0.91],
           [0.91, 3.8 , 0.  , 2.35, 1.44]])
    >>> similarities = aa.predict((0, 1))
    >>> similarities.round(2)
    0.91
    >>> similarities = aa.predict([(0, 1), (1, 2)])
    >>> similarities.round(2)
    array([0.91, 0.  ])

    References
    ----------
    Adamic, L. A., & Adar, E. (2003). `Friends and neighbors on the web.
    <https://www.sciencedirect.com/science/article/pii/S0378873303000091>`_
    Social networks, 25(3), 211-230.
    """
    def __init__(self):
        super(AdamicAdar, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(adamic_adar(self.indptr_, self.indices_, np.int32(source), np.array(targets, dtype=np.int32)))


class ResourceAllocation(FirstOrder):
    """Link prediction by Resource Allocation index:

    :math:`s(i, j) = \\underset{z \\in \\Gamma_i \\cap \\Gamma_j}{\\sum} \\dfrac{1}{|\\Gamma_z|}`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> ra = ResourceAllocation()
    >>> similarities = ra.fit_predict(adjacency, 0)
    >>> similarities.round(2)
    array([0.67, 0.33, 0.33, 0.33, 0.33])
    >>> similarities = ra.predict([0, 1])
    >>> similarities.round(2)
    array([[0.67, 0.33, 0.33, 0.33, 0.33],
           [0.33, 1.33, 0.  , 0.83, 0.5 ]])
    >>> similarities = ra.predict((0, 1))
    >>> similarities.round(2)
    0.33
    >>> similarities = ra.predict([(0, 1), (1, 2)])
    >>> similarities.round(2)
    array([0.33, 0.  ])

    References
    ----------
    Martínez, V., Berzal, F., & Cubero, J. C. (2016).
    `A survey of link prediction in complex networks.
    <https://dl.acm.org/doi/pdf/10.1145/3012704>`_
    ACM computing surveys (CSUR), 49(4), 1-33.
    """
    def __init__(self):
        super(ResourceAllocation, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        return np.asarray(resource_allocation(self.indptr_, self.indices_, np.int32(source),
                                              np.array(targets, dtype=np.int32)))


class PreferentialAttachment(FirstOrder):
    """Link prediction by Preferential Attachment index:

    :math:`s(i, j) = |\\Gamma_i||\\Gamma_j|`.

    Attributes
    ----------
    indptr_ : np.ndarray
        Pointer index for neighbors.
    indices_ : np.ndarray
        Concatenation of neighbors.

    Examples
    --------
    >>> from sknetwork.data import house
    >>> adjacency = house()
    >>> pa = PreferentialAttachment()
    >>> similarities = pa.fit_predict(adjacency, 0)
    >>> similarities
    array([4, 6, 4, 4, 6], dtype=int32)
    >>> similarities = pa.predict([0, 1])
    >>> similarities
    array([[4, 6, 4, 4, 6],
           [6, 9, 6, 6, 9]], dtype=int32)
    >>> similarities = pa.predict((0, 1))
    >>> similarities
    6
    >>> similarities = pa.predict([(0, 1), (1, 2)])
    >>> similarities
    array([6, 6], dtype=int32)

    References
    ----------
    Albert, R., Barabási, L. (2002). `Statistical mechanics of complex networks
    <https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.74.47>`_
    Reviews of Modern Physics.
    """
    def __init__(self):
        super(PreferentialAttachment, self).__init__()

    def _predict_base(self, source: int, targets: Iterable):
        """Prediction for a single node."""
        deg_src = self.indptr_[source+1] - self.indptr_[source]
        tgt = np.array(targets)
        deg_tgt = self.indptr_[tgt+1] - self.indptr_[tgt]
        return deg_src * deg_tgt
