from pathlib import Path
from pyvis.network import Network
import networkx as nx
import numpy as np
from collections import defaultdict
from pprint import pprint
from typing import Any

Input = dict[str, set[str]]

INPUT_FILE_PATH = Path("input.txt")

TO_CUT = [
    ("qfj", "tbq"),
    ("qqh", "xbl"),
    ("dsr", "xzn"),
]

# TO_CUT = [
#     ("hfx", "pzl"),
#     ("bvb", "cmg"),
#     ("nvd", "jqt"),
# ]


def read_input() -> Input:
    graph = defaultdict(set)
    with open(INPUT_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            head, others = line.strip().split(":")
            head = head.strip()
            for other in others.strip().split():
                other = other.strip()
                graph[head].add(other)
                graph[other].add(head)
    return graph


def solve(graph: Input) -> Any:
    n = len(graph)

    # g = nx.from_dict_of_lists(graph)
    # net = Network(notebook=True)
    # net.from_nx(g)
    # net.show("example.html")
    # nx.draw_spectral(g)

    # index_to_node = list(graph.keys())
    # node_to_index = {node: i for i, node in enumerate(index_to_node)}
    # n = len(index_to_node)
    # adjacency = np.zeros((n, n), dtype=float)
    # for head, others in graph.items():
    #     head_index = node_to_index[head]
    #     for other in others:
    #         other_index = node_to_index[other]
    #         adjacency[head_index, other_index] = 1
    # laplacian = np.identity(n) * np.sum(adjacency, axis=0) - adjacency
    # eig = np.linalg.eig(laplacian)
    # eig_sort = np.argsort(eig.eigenvalues)
    # eigenvalues = eig.eigenvalues[eig_sort]
    # eigenvectors = eig.eigenvectors[eig_sort]
    # print(eig)

    for node_a, node_b in TO_CUT:
        graph[node_a].remove(node_b)
        graph[node_b].remove(node_a)
    seen = set()
    to_search = {next(iter(graph))}
    while len(to_search) > 0:
        loc = to_search.pop()
        seen.add(loc)
        for neighbor in graph[loc]:
            if neighbor not in seen:
                to_search.add(neighbor)

    n_group_a = len(seen)
    n_group_b = n - n_group_a
    return n_group_a * n_group_b


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
