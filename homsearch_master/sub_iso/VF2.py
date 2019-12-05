import networkx as nx
import networkx.algorithms.isomorphism as iso
import igraph as ig
import graph_tool.topology as gt
from itertools import combinations

"""
Based on VF2 algorithm count the number of subgraphs for a given graph H in G.
The spatial complexity is of order O(V), where V is the (maximum) number of vertices of the two graphs. 
Time complexity is O(V^2) in the best case and O(V!×V) in the worst case.

Try with different implementation packages: NetworkX, python-igraph and graph-tool.

subgraph isomorphism problem is NP-complete whereas the graph isomorphism problem is most likely not NP-complete.
"""


### NetworkX #########################################
### G1 and G2 are graph-subgraph isomorphic is to say that a subgraph of G1 is isomorphic to G2.
### "subgraph" here means a node-induced subgraph
### For subgraphs which are not induced, the term ‘monomorphism’ is preferred over ‘isomorphism’.
def count_isomorphisms_nx(H, G):
    """Returns the number of isomorphisms between given graphs H and G"""
    GM = iso.GraphMatcher(G1=H, G2=G)
    return len([m for m in GM.isomorphisms_iter()])


def count_subgraph_isomorphisms_nx(H, G):
    """Given a pattern F, counts the number of isomorphisms between F and induced subgraphs of G and returns it."""
    GM = iso.GraphMatcher(G1=G, G2=H)
    return len([m for m in GM.subgraph_isomorphisms_iter()])


# def count_subgraph_monomorphisms_nx(H, G):
#     sub_iso = 0
#     for vlist in combinations(G.nodes, H.number_of_nodes()):
#         ### induced subgraphs
#         g_indsub = nx.Graph(nx.subgraph(G, vlist))
#         for elist in combinations(g_indsub.edges, H.number_of_edges()):
#             ### subgraphs
#             g_sub = nx.Graph()
#             g_sub.add_nodes_from(nodes_for_adding=vlist)
#             g_sub.add_edges_from(ebunch_to_add=elist)
#             sub_iso += count_isomorphisms_nx(H, g_sub)
#     return sub_iso

def count_subgraph_monomorphisms_nx(H, G):
    """https://www.osgeo.cn/networkx/_modules/networkx/algorithms/isomorphism/isomorphvf2.html"""
    GM = iso.GraphMatcher(G1=G, G2=H)
    return len([m for m in GM.subgraph_monomorphisms_iter()])


def count_induced_subgraphs_nx(H, G):
    """#IndSub(H, G)"""
    return int(count_subgraph_isomorphisms_nx(H, G) / count_isomorphisms_nx(H, H))


def count_subgraphs_nx(F, G):
    """#Sub(H, G): the number of subgraphs of G that are isomorphic to H"""
    return int(count_subgraph_monomorphisms_nx(F, G) / count_isomorphisms_nx(F, F))


### Python-igraph #########################################
def count_subgraph_isomorphisms_ig(F, G):
    # print([e.tuple for e in G.es])
    # print([v.index for v in G.vs])
    sub_iso = 0
    for vlist in combinations([v.index for v in G.vs], F.vcount()):
        ### induced subgraph
        g_indsub = G.induced_subgraph(vertices=vlist, implementation="create_from_scratch")
        for elist in combinations([e.tuple for e in g_indsub.es], F.ecount()):
            ### subgraphs
            g_sub = ig.Graph.TupleList(edges=elist)
            sub_iso += F.count_isomorphisms_vf2(g_sub)
    return sub_iso


def count_subgraphs_ig(F, G):
    return int(count_subgraph_isomorphisms_ig(F, G) / F.count_automorphisms_vf2())


def count_subgraphs_vf2_ig(F, G):
    return int(G.count_subisomorphisms_vf2(F) / F.count_automorphisms_vf2())


def count_subgraphs_lad_ig(F, G):
    return int(len(G.get_subisomorphisms_lad(F, induced=False)) / F.count_automorphisms_vf2())


def count_motif_ig(F, size=3):
    """
    This function counts the total number of motifs in a graph without assigning isomorphism classes to them.
    :param F:
    :param size: size of motif (3 or 4)
    :return:
    """
    return F.motifs_randesu_no(size=size, cut_prob=None)


### graph-tool #########################################
def count_subgraphs_gt(F, G):
    return int(len(gt.subgraph_isomorphism(F, G, induced=False)) / len(gt.subgraph_isomorphism(F, F, subgraph=False)))
