import time
import networkx as nx
# import igraph as ig
# import graph_tool.all as gt
import numpy as np
from multiprocessing import Pool
from func_timeout import func_set_timeout
# TODO: from homlib import Graph, hom
# from homlib import Graph, hom
from utilities.partition import partition, multiplier_list, partition_with_iso_checking
from homsearch_master.homsearch import find_homomorphisms
from homsearch_master.sub_iso import VF2, VF3

##################### homsearch_master + GMP ######################
# @profile
def sub_GMP(H, G):
    partition_dict_all = partition(H)
    graph_list = list(partition_dict_all.values())
    partition_list = [eval(p) for p in list(partition_dict_all.keys())]
    mul_list = multiplier_list(partition_list)
    # hom_list = [find_homomorphisms(g, G, only_count=True) for g in graph_list]
    ### divide H and G into connected components
    hom_list = []
    for h in graph_list:
        hom = 1
        for h_c in nx.connected_components(h):
            hom_ = 0
            for g_c in nx.connected_components(G):
                hom_ += find_homomorphisms(h.subgraph(h_c), G.subgraph(g_c), only_count=True)
            hom *= hom_
        hom_list.append(hom)
    num_sub = int(np.dot(np.array(mul_list), np.array(hom_list)) / VF2.count_isomorphisms_nx(H, H))

    return num_sub


def sub_GMP_with_iso_checking(H, G):
    graph_list, mul_list = partition_with_iso_checking(H)
    hom_list = []
    for h in graph_list:
        hom = 1
        for h_c in nx.connected_components(h):
            hom_ = 0
            for g_c in nx.connected_components(G):
                hom_ += find_homomorphisms(h.subgraph(h_c), G.subgraph(g_c), only_count=True)
            hom *= hom_
        hom_list.append(hom)
    num_sub = int(np.dot(np.array(mul_list), np.array(hom_list)) / VF2.count_isomorphisms_nx(H, H))

    return num_sub


def GMP(H_list, G, checking=True):
    start = time.time()
    result = []
    if checking:
        for h in H_list:
            result.append(sub_GMP_with_iso_checking(h, G))
    else:
        for h in H_list:
            result.append(sub_GMP(h, G))
    t = time.time() - start
    print('Running time: %.2f seconds' % t)
    return result, t


def GMP_multiprocess(H_list, G, checking=True, n_jobs=4):
    start = time.time()
    pool = Pool(processes=n_jobs)
    p = [0] * len(H_list)
    if checking:
        for i, h in enumerate(H_list):
            p[i] = pool.apply_async(sub_GMP_with_iso_checking, args=(h, G))
    else:
        for i, h in enumerate(H_list):
            p[i] = pool.apply_async(sub_GMP, args=(h, G))
    pool.close()
    pool.join()
    t = time.time() - start

    result = []
    for i in range(len(H_list)):
        result.append(p[i].get())
    print('Running time: %.2f seconds' % t)
    return result, t


##################### homlib + GMP ######################
def graph_trans(G):
    G_ = Graph(nx.number_of_nodes(G))
    for e in G.edges:
        G_.addEdge(e[0], e[1])
    return G_


def sub_GMP_homlib(F, G):
    partition_dict = partition(F)
    graph_list = list(partition_dict.values())
    mul_list = multiplier_list(partition_dict)
    G_ = graph_trans(G)
    hom_list = []
    for g in graph_list:
        hom_list.append(hom(graph_trans(g), G_))
        #TODO: divide g and G_ into connected components
    num_sub = int(np.dot(np.array(mul_list), np.array(hom_list)) / VF2.count_isomorphisms_nx(F, F))

    return num_sub


##################### VF2 ######################
@func_set_timeout(1000)
def VF_2(H_list, G):
    result = []
    start = time.time()
    for h in H_list:
        result.append(VF2.count_subgraphs_nx(h, G))
    t = time.time() - start
    print('Running time: %.2f seconds' % t)
    return result, t


@func_set_timeout(600)
def VF_2_multiprocess(H_list, G, n_jobs=4):
    start = time.time()
    pool = Pool(processes=n_jobs)
    p = [0] * len(H_list)
    for i, h in enumerate(H_list):
        p[i] = pool.apply_async(VF2.count_subgraphs_nx, args=(h, G))
    pool.close()
    pool.join()
    t = time.time() - start

    result = []
    for i in range(len(H_list)):
        result.append(p[i].get())
    print('Running time: %.2f seconds' % t)
    return result, t


##################### VF3 ######################
@func_set_timeout(1000)
def VF_3(H_list, G, filename=None):
    result = []
    start = time.time()
    for h in H_list:
        result.append(VF3.count_subgraphs(h, G, filename))
    t = time.time() - start
    print('Running time: %.2f seconds' % t)
    return result, t


@func_set_timeout(1800)
def VF_3_multiprocess(H_list, G, n_jobs=4):
    start = time.time()
    pool = Pool(processes=n_jobs)
    p = [0] * len(H_list)
    for i, h in enumerate(H_list):
        filename = '{}'.format(i)
        p[i] = pool.apply_async(VF3.count_subgraphs, args=(h, G, filename))
    pool.close()
    pool.join()
    t = time.time() - start

    result = []
    for i in range(len(H_list)):
        result.append(p[i].get())
    print('Running time: %.2f seconds' % t)
    return result, t

