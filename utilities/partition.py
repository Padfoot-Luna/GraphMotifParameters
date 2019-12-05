import networkx as nx
from collections import defaultdict
from itertools import combinations
import math


def A(G):
    """
    Given a graph G,
    combine every pair of nonadjacent nodes as a new node and get the corresponding node partition as a set of lists,
    return all possible node partitions as a list.
    """
    partition_list = []
    #     for i in set(combinations(G.nodes, 2)) - set(G.edges):  # set of tuples
    for i in set(nx.non_edges(G)):
        partition = []
        partition.append(set(i))
        for v in set(G.nodes) - set(i):
            partition.append({v})
        partition_list.append(partition)
    return partition_list


def B(partition_list):
    """from partition list get node mapping list """
    node_mapping_list = []
    for partition in partition_list:
        g = nx.Graph()
        g.add_nodes_from(range(len(partition)))
        node_mapping = defaultdict(set)
        node_mapping.update(zip(g.nodes, partition))
        node_mapping_list.append(node_mapping)
    return node_mapping_list


def takeMin(elem):
    e = list(elem)
    e.sort()
    return e[0]


def C(G, node_mapping):
    """
    Given a graph, the node_mapping from its parent,
    generate its node partition list by A,
    return a dict with generated graphs as the keys and parent-child node mappings as values
    and a dict with node partition of G as key and the child graph as value
    """
    node_mapping_dict = {}  # node index: set(node indices)
    partition_dict = {}
    partition_list = A(G)
    node_mapping_list = B(partition_list)

    for i, partition in enumerate(partition_list):
        ### graph generation
        g = nx.Graph()
        g.add_nodes_from(range(len(partition)))  # nodes
        edge_list = list(combinations(g.nodes, 2))
        for e, edge in enumerate(combinations(partition, 2)):
            if G.subgraph(edge[0] | edge[1]).size() > 0:
                g.add_edges_from([edge_list[e]])  # edge
        ### final child-ancestor node mapping
        for k, v in node_mapping_list[i].items():
            node_mapping_list[i][k] = set.union(*[node_mapping[_] for _ in v])
        node_mapping_dict[g] = node_mapping_list[i]
        p = list(node_mapping_list[i].values())
        p.sort(key=takeMin)
        partition_dict[str(p)] = g

    return node_mapping_dict, partition_dict


def D(node_mapping_dict):
    """get next_node_mapping_dict and next_partition_dict"""
    graph_list = list(node_mapping_dict.keys())
    next_node_mapping_dict, next_partition_dict = {}, {}
    for g in graph_list:
        new_node_mapping_dict, new_partition_dict = C(g, node_mapping_dict[g])
        next_node_mapping_dict.update(new_node_mapping_dict)
        next_partition_dict.update(new_partition_dict)

    node_mapping_dict = {}
    for key, value in next_partition_dict.items():
        node_mapping_dict[value] = next_node_mapping_dict[value]
    return node_mapping_dict, next_partition_dict


def E(node_mapping_dict):
    """delete isomorphic graphs"""
    graph_list = list(node_mapping_dict.keys())

    while len(graph_list) > 0:
        g = graph_list[0]
        for g_ in graph_list[1:]:
            if nx.is_isomorphic(g, g_):
                node_mapping_dict.pop(g_)
                graph_list.remove(g_)
        graph_list.remove(g)

    return node_mapping_dict


def partition(G):
    ### init
    # node_mapping_dict_all = {}
    partition_dict_all = {}
    ### G
    partition = [{v} for v in G.nodes()]  # P0
    partition_dict_all[str(partition)] = G
    node_mapping_dict = {G: B([partition])[0]}
    # node_mapping_dict_all.update(node_mapping_dict)
    partition_list = A(G)  # P1

    ### iteration
    while len(partition_list) > 0:
        node_mapping_dict, partition_dict = D(node_mapping_dict)
        partition_dict_all.update(partition_dict)
        #     node_mapping_dict_all.update(node_mapping_dict)

        partition_list = []
        for g in node_mapping_dict.keys():
            partition_list.extend(A(g))

    return partition_dict_all


def multiplier_list(partition_list):
    num_v = len(partition_list[0])
    mul_list = [1]
    for p in partition_list[1:]:
        mul = 1
        for n in p:
            mul *= math.factorial(len(n)-1)
        mul_list.append((-1)**(num_v - len(p)) * mul)
    return mul_list


def multiplier_dict(partition_dict_all):
    partition_list = [eval(p) for p in list(partition_dict_all.keys())]
    mul_list = multiplier_list(partition_list)
    mul_dict = dict(zip(partition_dict_all.keys(), mul_list))
    return mul_dict


def partition_with_iso_checking(G):
    """
    Combine isomorphic graphs among partition(G) and add corresponding multipliers to avoid repeated #hom
    1. graphs are grouped by |V| and |E|
    2. iterate until number of pair-wise isomorphisms become 0
    3. return new partition_dict and multiplier
    """
    partition_dict_all = partition(G)
    mul_dict = multiplier_dict(partition_dict_all)
    ### init
    keys = dict()
    for k, v in partition_dict_all.items():
        keys['{}_{}'.format(nx.number_of_nodes(v), nx.number_of_edges(v))] = []
    for k, v in partition_dict_all.items():
        keys['{}_{}'.format(nx.number_of_nodes(v), nx.number_of_edges(v))].append(k)
    v_e = set()
    for k, v in keys.items():
        if len(v) > 1:
            v_e.add(k)
    checked = set()
    ### iteration
    while len(v_e) > 0:
        for k in v_e:
            count = 0
            for u, v in combinations(keys[k], 2):
                if nx.is_isomorphic(partition_dict_all[u], partition_dict_all[v]):
                    partition_dict_all.pop(v, None)
                    mul_dict[u] += mul_dict[v]
                    mul_dict.pop(v, None)
                    break
                else:
                    count += 1
            if count == len(keys[k]) * (len(keys[k]) - 1) / 2:  # no isomorphism
                checked.add(k)
        keys = dict()
        for k, v in partition_dict_all.items():
            keys['{}_{}'.format(nx.number_of_nodes(v), nx.number_of_edges(v))] = []
        for k, v in partition_dict_all.items():
            keys['{}_{}'.format(nx.number_of_nodes(v), nx.number_of_edges(v))].append(k)
        v_e = set()
        for k, v in keys.items():
            if len(v) > 1:
                v_e.add(k)
        v_e -= checked

    return list(partition_dict_all.values()), list(mul_dict.values())




