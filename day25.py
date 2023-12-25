import math
from collections import Counter, defaultdict
from pathlib import Path
from pprint import pprint

import numpy as np

Input = dict[str, set[str]]

INPUT_FILE_PATH = Path("input.txt")


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
    # 1. calculate fiedler vector (eigenvector of 2nd-smallest eigenvalue of laplacian)
    # 2. use its values as 1-dimensional locations for graph nodes
    # 3. find edges that connect nodes that are on opposite sides of 0
    eig = np.linalg.eig(laplacian)
    eig_sort = np.argsort(eig.eigenvalues)
    eigenvectors = eig.eigenvectors.T[eig_sort]
    fiedler = eigenvectors[1]
    # count partition sizes
    counts = Counter(fiedler >= 0)
    return math.prod(counts.values())


def main():
    input_ = read_input()
    answer = solve(input_)
    pprint(answer)


if __name__ == "__main__":
    main()
