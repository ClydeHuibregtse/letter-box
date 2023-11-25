
import os
from typing import List, Optional

from .utils import (
    build_letters,
)
from .games import Game
from .oracles import Oracle
from .graphs import (
    Trajectory,
    GraphNode
)


def solve(
    letters: Optional[List[str]] = None,
    S: Optional[int] = None,
    N: int = 1_000,
    depth: int = 1,
    graph_dir: Optional[str] = None
):

    # Auto-construct letters if not provided
    if letters is None:
        assert S is not None, "If letters are not provided, S must be provided"
        letters = build_letters(S)

    # Build the game and an oracle
    game = Game.new(letters)
    oracle = Oracle(game)
    print(game.to_ascii())

    best_trajectory: Optional[Trajectory] = None

    # Try each starting point
    for i, l in enumerate(letters):
        print(f"Starting letter: {l} at index {i}")

        # Start at 1.0 temperature and decrease each new trajectory
        T = 1.0
        for t_idx in range(N):

            # Start a new node
            node = GraphNode.new(game, i, oracle=oracle)
            t = Trajectory()
            # Iterate until we no longer get nodes or have reached a winning state
            while (visit := node.visit(T, depth_of_search=depth)) is not None:
                new_words, new_paths, new_nodes = visit
                t.add_words_states(new_words, new_paths, [n.state for n in new_nodes])

                # Depending on depth, we may have many nodes traveled on this visit, so
                # update our node to the last in the chain
                node = new_nodes[-1]

            if best_trajectory is None or (len(t.words) <= len(best_trajectory.words) and not t.is_fail()):
                best_trajectory = t
            # Increment our temperature
            T -= t_idx / N

        assert best_trajectory is not None, \
            f"No solution found for '{l}' at index {i}"

        print(l, best_trajectory, len(best_trajectory.words))

    # Render graph to CSV
    if graph_dir is not None:
        nodes, edges = oracle.graph_nodes_to_dfs()
        nodes.to_csv(os.path.join(graph_dir, "nodes.csv"), index=False)
        edges.to_csv(os.path.join(graph_dir, "edges.csv"), index=False)

    return letters, best_trajectory
