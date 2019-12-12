import os
import subprocess
import networkx as nx
from itertools import combinations
from homsearch_master.sub_iso import VF2
from utilities.load_data import nx_to_grf

### cmd
# sub_iso/vf3 sub_iso/vflib3/test/bvg1.sub.grf sub_iso/vflib3/test/bvg1.grf
# sub_iso/vf3 dataset/vf3/h.grf dataset/vf3/g.grf


def count_subgraph_isomorphisms(H, G, filename=None):
    path = os.path.abspath("..")
    path = os.path.join(path, "dataset/vf3")
    if filename != None:
        path = os.path.join(path, filename)
        if not os.path.exists(path):
            os.mkdir(path)
    filename_h = os.path.join(path, 'h.grf')
    filename_g = os.path.join(path, 'g.grf')
    nx_to_grf(H, filename_h)
    nx_to_grf(G, filename_g)

    cmd = "sub_iso/vf3 {} {}"  ### induced subgraph isomorphisms
    try:
        out_1 = subprocess.check_output(cmd.format(filename_h, filename_g), shell=True, stderr=subprocess.STDOUT)
        out_1 = out_1.decode('utf-8')
        return eval(out_1.split(" ")[0])
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


def count_induced_subgraphs(H, G, filename=None):
    path = os.path.abspath("..")
    path = os.path.join(path, "dataset/vf3")
    if filename != None:
        path = os.path.join(path, filename)
        if not os.path.exists(path):
            os.mkdir(path)
    filename_h = os.path.join(path, 'h.grf')
    filename_g = os.path.join(path, 'g.grf')
    nx_to_grf(H, filename_h)
    nx_to_grf(G, filename_g)

    cmd = "sub_iso/vf3 {} {}"
    try:
        out_1 = subprocess.check_output(cmd.format(filename_h, filename_g), shell=True, stderr=subprocess.STDOUT)
        out_2 = subprocess.check_output(cmd.format(filename_h, filename_h), shell=True, stderr=subprocess.STDOUT)
        out_1 = out_1.decode('utf-8')
        out_2 = out_2.decode('utf-8')
        return int(eval(out_1.split(" ")[0]) / eval(out_2.split(" ")[0]))
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


def count_subgraphs(H, G, filename=None):
    """Sub = Ext * IndSub (7)(8)"""
    n = nx.number_of_nodes(H)
    extensions = {}
    for add_e in range(1, int(n * (n - 1) / 2) - nx.number_of_edges(H) + 1):
        F_dict = {}
        for e_list in combinations(set(nx.non_edges(H)), add_e):
            F = H.copy()
            F.add_edges_from(e_list)
            F_dict[F] = 1
        ### iso checking
        count = len(F_dict) * (len(F_dict) - 1) / 2
        while count > 0:
            for g1, g2 in combinations(F_dict.keys(), 2):
                if nx.is_isomorphic(g1, g2):
                    F_dict[g1] += F_dict[g2]
                    F_dict.pop(g2, None)
                    count = len(F_dict) * (len(F_dict) - 1) / 2
                    break
                else:
                    count -= 1

        extensions.update(F_dict)

    num_sub = count_induced_subgraphs(H, G, filename)
    for F, ext in extensions.items():
        #     num_sub += ext * VF3.count_induced_subgraph(F, G)
        num_sub += VF2.count_subgraphs_nx(H, F) * count_induced_subgraphs(F, G, filename)
    return int(num_sub)

