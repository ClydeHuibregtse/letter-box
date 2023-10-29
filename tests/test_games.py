
from letter_box.solve import (
    solve
)

from letter_box.utils import (
    RNG,
    build_letters
)
from letter_box.games import Game
from letter_box.graph_solutions import GraphNode


def test_game_ascii_render():
    """Test that Game objects are properly rendered to ascii chars"""

    # Give ourselves a valid board and state vector to see visualization
    S = 10
    letters = build_letters(S)
    game = Game.new(letters)
    game.state = [RNG.random() < 0.5 for _ in range(len(letters))]
    print(game.to_ascii())


def test_graph_nodes():
    """Test the implementation of the GraphNode class"""
    # Build an example game
    S = 3
    letters = build_letters(S)
    game = Game.new(letters)

    # Construct a graph node
    n = GraphNode.new(
        game,
        1
    )

    # Visit this node and evaluate what edges come out
    new_words, new_paths, nodes = n.visit(1.0)
    node = nodes[0]
    # Check the behavior of variable depth of search
    assert len(node.edges) == 0
    node.find_edges()
    assert len(node.edges) > 0
    assert all(len(e_node.edges) == 0 for w, (s, e_node, e_path) in node.edges.items())

    new_words, new_paths, nodes = n.visit(1.0)
    node = nodes[0]
    node.find_edges(depth_of_search=2)
    assert len(node.edges) > 0
    assert all(len(e_node.edges) > 0 for w, (s, e_node, e_path) in node.edges.items())

    # Try out computing scores
    scores = node.compute_scores()  # Single depth of search
    assert len(scores) == len(node.edges)

    double_scores = node.compute_scores(depth_of_search=2)
    assert len(double_scores) == sum(len(e_node.edges) for w, (s, e_node, e_path) in node.edges.items())


def test_trajectory():
    """Tests the implementation of Trajectory"""
    solve(S=5, N=10)


if __name__ == "__main__":
    test_trajectory()
