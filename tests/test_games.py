
from letter_box.solve import (
    solve
)

from letter_box.utils import (
    RNG,
    build_letters
)
from letter_box.games import Game
from letter_box.graphs import GraphNode


def test_game_ascii_render():
    """Test that Game objects are properly rendered to ascii chars"""

    # Give ourselves a valid board and state vector to see visualization
    S = 10
    letters = build_letters(S)
    game = Game.new(letters)
    game.state = int(RNG.random() * 2 ** 32)
    print(game.to_ascii())


def test_graph_nodes():
    """Test the implementation of the GraphNode class"""
    # Build an example game
    S = 2
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
    # Search for all new edges leaving from this node
    # NOTE: The oracle caches all nodes it's seen, so it's possible
    #       that one of these edges is node itself. Consider any
    #       palindrome that introduces no new letters to the covered
    #       state of the game.
    node.find_edges()
    assert len(node.edges) > 0
    assert all(
        len(e_node.edges) == 0
        for w, (s, e_node, e_path) in node.edges.items()
        # There's a chance we end up back at the same GraphNode, node.
        # Exclude that here.
        if e_node != node
    )

    node = GraphNode.new(
        game,
        1
    )
    node.find_edges(depth_of_search=2)
    assert len(node.edges) > 0
    assert all(len(e_node.edges) > 0 for w, (s, e_node, e_path) in node.edges.items())

    # Try out computing scores
    scores = node.compute_scores()  # Single depth of search
    # We should get a score for every edge that does not form a cycle, which for a depth of 1,
    # amounts to just the unique nodes in our edge set
    assert len(scores) == len(set(e_node for w, (s, e_node, e_path) in node.edges.items()))

    # With a depth of 2, the number of scores we compute is equal to the total number of
    # unique nodes visited in the double search
    seen = set()
    double_scores = node.compute_scores(depth_of_search=2, seen=seen)
    # All scores should be of length-2
    assert all(len(s) == 2 for s in double_scores)

    # Collect all of the unique nodes between the root and 2 layers
    depth_1_nodes = set()
    depth_2_nodes = set()
    for w1, (s1, e_node1, e_path1) in node.edges.items():
        depth_1_nodes.add(e_node1)
        for w2, (s2, e_node2, e_path2) in e_node1.edges.items():
            depth_2_nodes.add(e_node2)

    unique_nodes = depth_1_nodes | depth_2_nodes
    # Our "seen" hash should differ only by the root
    assert seen - unique_nodes == {node}

    # At most, every double score results in a unique depth-2 node
    # (i.e., there are no nodes 2 away from the root that are also 1 away)
    assert len(double_scores) <= len(depth_2_nodes)
    # But we should always have at least as many length-1 scores as
    # we do depth-1 nodes
    assert len(double_scores) >= len(depth_1_nodes)


def test_trajectory():
    """Tests the implementation of Trajectory"""
    N = 10
    import time
    now = time.time()
    for _ in range(N):
        solve(S=5, N=10)
    print((time.time() - now) / N)


if __name__ == "__main__":
    test_trajectory()
