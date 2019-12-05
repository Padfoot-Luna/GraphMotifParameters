from typing import List, Tuple, Dict
import networkx as nx


def extract_edge_list_from_edgelist(edge_list_file, sep='') -> List[Tuple]:
    edge_list = []
    with open(edge_list_file, 'r') as f:
        for line in f:
            if line[0] == '%':
                continue
            source, target = line.strip().split(sep)
            edge_list.append((int(source), int(target)))
    return edge_list


def extract_edge_list_from_adjlist(adjlist: List[Dict[int, set]]) -> List[Tuple]:
    edge_list = []
    for i in range(len(adjlist)):
        for neighbor in adjlist[i][i]:
            if neighbor > i:
                edge_list.append((i, neighbor))
    return edge_list


def timeout_check(t_list, limit):
    for i, t in enumerate(t_list):
        if isinstance(t, str):
            t_list[i] = limit
    return t_list


"""
https://mivia.unisa.it/datasets/graph-database/vf3-library/vf3-usage/
The format of the file containing the graph is the following:

“number of nodes”
“id_node 0” “label”
“id_node 1” “label”
“id_node 2” “label”
…
“number of edges”
“id_starting_node 0” “id_ending_node” “label edge”*
“id_starting_node 0” “id_ending_node” “label edge”*
…
“number of edges”
“id_starting_node 1” “id_ending_node” “label edge”*
“id_starting_node 1” “id_ending_node” “label edge”*
"""
def nx_to_grf(G, filename, i=0):
    """node index starts from i"""
    with open(filename, 'w') as f:
        f.write(str(nx.number_of_nodes(G)))
        f.write('\n')
        for v in nx.nodes(G):
            f.write('%d %d' % (v - i, 1))
            f.write('\n')
        for v in nx.nodes(G):
            f.write(str(nx.degree(G, nbunch=v)))
            f.write('\n')
            for u in nx.neighbors(G, v):
                f.write('%d %d' % (v - i, u - i))
                f.write('\n')
    return filename
