"""
La idea de este archivo es ejecutar el algoritmo de conexion-contraccion para calcular el tamaño
del árbol y el numérico cromático del grafo.
Está pensado para corroborar que un ejercicio de conexión-contracción no sea demasiado largo para
resolver si no se utiliza poda (i.e. si se busca el polinomio cromático).
"""

import networkx as nx
from itertools import chain


def contraction(G, a, b):
    H = G.copy()
    new_vertex = a + b
    for c in chain(H.neighbors(a), H.neighbors(b)):
        H.add_edge(new_vertex, c)
    H.remove_node(a)
    H.remove_node(b)
    return H


def connection(G, a, b):
    H = G.copy()
    H.add_edge(a, b)
    return H


def color(G, g_ls, q):
    n = G.number_of_nodes()
    if G.number_of_edges() == n * (n - 1) // 2:
        q = min(n, q)
    else:
        for c in G.nodes:
            try:
                x, y = nx.maximal_independent_set(G, [c])[:2]
            except ValueError:
                continue
            else:
                break
        G1 = contraction(G, x, y)
        G2 = connection(G, x, y)
        g_ls.extend([G1, G2])
        q = min(color(G1, g_ls, q), color(G2, g_ls, q))
    return q


def zykov_tree(G):
    """ Para coloreo de grafos, calcula cuantos grafos son necesarios para el algoritmo de conexión-contracción """
    n = G.number_of_nodes()
    graph_ls = []
    num_cromatico = color(G, graph_ls, n)
    return num_cromatico, graph_ls


def ejemplo():
    G = nx.Graph()
    es = {('a', 'b'), ('a', 'c'), ('b', 'c'), ('b', 'e'), ('b', 'd'), ('d', 'e'), ('c', 'e'), ('c', 'f'), ('e', 'f')}
    G.add_edges_from(es)
    num_crom, ls = zykov_tree(G)
    print(num_crom, len(ls))


if __name__ == '__main__':
    ejemplo()
