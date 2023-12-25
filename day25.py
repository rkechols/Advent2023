import copy
import math
from collections import Counter, defaultdict
from pathlib import Path
from pprint import pprint

import numpy as np

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


def solve(graph: Input) -> int:
    n = len(graph)
    # assign indices to nodes
    index_to_node = list(graph.keys())
    node_to_index = {node: i for i, node in enumerate(index_to_node)}
    # make adjacency and laplacian matrices
    adjacency = np.zeros((n, n), dtype=int)
    for head, others in graph.items():
        head_index = node_to_index[head]
        for other in others:
            other_index = node_to_index[other]
            adjacency[head_index, other_index] = 1
    laplacian = np.identity(n, dtype=int) * np.sum(adjacency, axis=0) - adjacency
    # wizardry:
    # 1. calculate fiedler vector
    # 2. use its values as 1-dimensional locations for graph nodes
    # 3. find edges that connect nodes that are on opposite sides of 0
    eig = np.linalg.eig(laplacian)
    eig_sort = np.argsort(eig.eigenvalues)
    eigenvectors = eig.eigenvectors.T[eig_sort]
    fiedler = eigenvectors[1]
    to_cut = set()
    for head, others in graph.items():
        head_index = node_to_index[head]
        for other in others:
            other_index = node_to_index[other]
            f_low, f_high = sorted((fiedler[i] for i in (head_index, other_index)))
            if f_low <= 0 <= f_high and (other, head) not in to_cut:
                to_cut.add((head, other))
    assert len(to_cut) <= 3
    # cut the edges
    graph = copy.deepcopy(graph)
    for node_a, node_b in to_cut:
        print(f"cutting {node_a}/{node_b}")
        graph[node_a].remove(node_b)
        graph[node_b].remove(node_a)
    # figure out the new graph components
    seen = set()
    connected_groups = []
    for search_node in graph:
        if search_node in seen:
            continue
        to_search = {search_node}
        connected = set()
        while len(to_search) > 0:
            loc = to_search.pop()
            seen.add(loc)
            connected.add(loc)
            for neighbor in graph[loc]:
                if neighbor not in seen:
                    to_search.add(neighbor)
        connected_groups.append(connected)
    assert len(connected_groups) == 2
    return math.prod(len(group) for group in connected_groups)


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
