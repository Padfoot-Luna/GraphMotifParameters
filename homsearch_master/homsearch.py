# Copyright (c) 2015 Tomas Gavenciak <gavento@ucw.cz>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from homsearch_interface import HomsearchInterface

#############################
# Auxiliary conversion utils


def graph_to_adjlist(G):
    "Takes a graph and returns a numeric adjacency list"

    # Work for Sage and NetworkX
    # try:
    #     Gvs = G.vertices()
    # except AttributeError:
    Gvs = list(G.nodes())

    map_numbers = {}
    for vi in range(G.order()):
        v = Gvs[vi]
        map_numbers[v] = vi

    adj_list = []
    for vi in range(G.order()):
        v = Gvs[vi]
        adj_list.append([map_numbers[u] for u in G.neighbors(v)])

    return adj_list


def fmap_to_graphmap(G, H, f):
    """
    Takes source and target Graphs and a numeric map (list) from homsearch_interface, returns G-H-vertex map.
    Vertices assigned -1 are given None
    """

    # Work for Sage and NetworkX
    # try:
    #     Gvs = G.vertices()
    # except AttributeError:
    Gvs = list(G.nodes())
    # try:
    #     Hvs = H.vertices()
    # except AttributeError:
    Hvs = list(H.nodes())

    gf = {}
    for v in range(len(f)):
        fv = f[v]
        if fv >= 0:
            gf[Gvs[v]] = Hvs[fv]
        else:
            gf[Gvs[v]] = None
    return gf


def graphmap_to_fmap(G, H, gf):
    """
    Takes source and target Graphs and a G-H-vertex map, returns a numeric map (list) for homsearch_interface.
    Undefined vertices and vertices mapped to None are assigned -1.
    """

    # Work for Sage and NetworkX
    # try:
    #     Gvs = G.vertices()
    # except AttributeError:
    Gvs = list(G.nodes())
    # try:
    #     Hvs = H.vertices()
    # except AttributeError:
    Hvs = list(H.nodes())

    H_map_numbers = {}
    for vi in range(H.order()):
        v = Hvs[vi]
        H_map_numbers[v] = vi

    f = []
    for v in Gvs:
        if (v not in gf) or (gf[v] is None):
            f.append(-1)
        else:
            f.append(H_map_numbers[gf[v]])

    return f


######################################
# Main interface to running homsearch_master

def find_homomorphisms(G, H, results_limit=-1, only_count=False, max_depth=-1, partmap=None):
    """
    Run G->H homomorphism search on undirected graphs `G` and `H`, return list of maps or their number (acc. to `only_count`),
    starting with `partmap` G-H-map if given.
    """

    assert not G.is_directed()
    assert not H.is_directed()

    hs = HomsearchInterface(graph_to_adjlist(G), graph_to_adjlist(H),
            results_limit, (not only_count), False, max_depth=max_depth)

    if partmap is None:
        hs.search()
    else:
        hs.search_from(graphmap_to_fmap(G, H, partmap))

    if only_count:
        return hs.result_count()
    else:
        return [fmap_to_graphmap(G, H, f) for f in hs.result_list()]


# A retraction is a homomorphism r from a graph G to a subgraph H of G such that r(v) = v for each vertex v of H.
# In this case the subgraph H is called a retract of G
def find_retracts(G, results_limit=-1, only_count=False, max_depth=-1, partmap=None):
    """
    Run retract search on undirected graph `G`, return list of maps or their number (acc. to `only_count`),
    starting with `partmap` G-H-map if given.
    NOTE: always finds the identity.
    """

    assert not G.is_directed()

    hs = HomsearchInterface(graph_to_adjlist(G), graph_to_adjlist(G),
            results_limit, (not only_count), True, max_depth=max_depth)

    if partmap is None:
        hs.search()
    else:
        hs.search_from(graphmap_to_fmap(G, G, partmap))

    if only_count:
        return hs.result_count()
    else:
        return [fmap_to_graphmap(G, G, f) for f in hs.result_list()]


