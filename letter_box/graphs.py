"""Various classes to support the implementation of the shortest path
graph algorithm"""
from typing import List, Dict, Tuple, Optional, Iterator, Set
from attrs import define, field
from collections import deque

import numpy as np

from .games import Game
from .oracles import Oracle
from .utils import RNG


@define
class DeepScore:
    words: List[str] = field()
    score: float = field()
    nodes: List["GraphNode"] = field()

    def __len__(self) -> int:
        return len(self.words)


@define()
class GraphNode:
    state: Game = field()
    # Consider what happens when two divergent trajectories return to a shared state with
    # a different "last_index" - I suspect this is not likely nor impactful to performance
    last_index: int = field()
    oracle: Oracle = field()
    edges: Dict[str, Tuple[float, "GraphNode", List[int]]] = field(factory=dict)

    _hash: int = field(default=0)

    @classmethod
    def new(
        cls, game: Game, last_index: int, oracle: Optional[Oracle] = None
    ) -> "GraphNode":
        oracle = oracle or Oracle(game)
        return GraphNode(game, last_index, oracle, hash=hash((game.state, last_index)))

    def __repr__(self) -> str:
        return f"GraphNode({self.state}, e={len(self.edges)}, i={self.last_index}, oracle={id(self.oracle)})"

    def __hash__(self) -> int:
        return self._hash

    def find_edges(self, depth_of_search: int = 1):
        # Once we've run out of layers, exit
        if depth_of_search == 0:
            return

        # Populate the edges that are pointed away from this node
        if len(self.edges) == 0:
            S = len(self.state.flat_letters) // 4
            self.edges = self.compute_edges(self.last_index, S)

        # Recurse depending on depth
        for w, (s, e_node, e_path) in self.edges.items():
            e_node.find_edges(depth_of_search=depth_of_search - 1)

    def compute_edges(
        self, last_index: int, S: int
    ) -> Dict[str, Tuple[float, "GraphNode", List[int]]]:
        edges = dict()
        for word in self.oracle.valid_words_by_letter(last_index):
            if (res := self.oracle.submit_word(self.state, word, last_index)) is None:
                continue
            next_state, path = res
            cached_node = self.oracle.get_graph_node(next_state.state, path[-1])
            if cached_node is None:
                next_node = GraphNode.new(next_state, path[-1], oracle=self.oracle)
                self.oracle.set_graph_node(next_state.state, path[-1], next_node)
            else:
                next_node = cached_node

            edges[word] = (GraphNode.transition_score(self, next_node), next_node, path)
        return edges

    def compute_scores(
        self, depth_of_search: int = 1, seen: Optional[Set["GraphNode"]] = None
    ) -> List["DeepScore"]:
        # Collect the DeepScores of length-"depth_of_search"
        scores = []

        # Implement a BFS over the nodes to search to a prescribed depth

        # The BFS should omit any path that intercepts a node we've seen at
        # an earlier depth
        if seen is None:
            seen = set()
        seen.add(self)

        # Create a queue of nodes to check
        #   Each element of the queue is a DeepScore, for the incremental
        #   nodes leading to the final node, from the root node.
        # So we begin with the empty DeepScore
        node_queue = deque([DeepScore([], 0, [])])
        while node_queue:
            # Get the DeepScore with the nodes whose edges we
            # should search next
            deep_score = node_queue.popleft()

            # If we have no nodes, we must be at the root
            n_visit = deep_score.nodes[-1] if len(deep_score) > 0 else self

            # If the path length is equal to the depth
            # (+1, since we start with the root node), compute the score
            # and append it to the scores
            if len(deep_score) == depth_of_search:
                scores.append(deep_score)

            # Otherwise, continue by adding all edge nodes to the queue
            # unless we've already been there, in which case there is
            # a guaranteed shorter path
            else:
                # TODO: reconcile what happens if edges is empty
                # (i.e., we haven't called find_edges to a sufficient depth)
                for w, (s, e, p) in n_visit.edges.items():
                    if e in seen:
                        continue
                    seen.add(e)

                    node_queue.append(
                        DeepScore(
                            deep_score.words + [w],
                            deep_score.score + s,
                            deep_score.nodes + [e],
                        )
                    )

        return scores

    @staticmethod
    def transition_score(n1: "GraphNode", n2: "GraphNode") -> float:
        """Return the score associated with transitioning from n1 to n2"""
        # Trajectories leave a scent that is the inverse of the the number of words it took to get there
        return float(n2.state.score() - n1.state.score())

    def visit(
        self, T: float, depth_of_search: int = 1
    ) -> Optional[Tuple[List[str], List[List[int]], List["GraphNode"]]]:
        if self.state.is_win():
            return None

        # Compute the edges out of this node, if they haven't
        # already been found
        self.find_edges(depth_of_search=depth_of_search)
        # Compute the depth_of_search score for each leaf node
        c_scores = self.compute_scores(depth_of_search=depth_of_search)
        scores = np.array(c_scores)

        # Select an edge probabilistically
        p_scores = np.array([s.score**10 for s in scores])

        # Add variance to the scores until we've refined our temperature
        sum_scores = p_scores.sum()
        if sum_scores == 0:
            return None
        p_scores /= sum_scores
        dscores = np.clip(RNG.random(len(p_scores)) * T, 0, 10)
        p_scores += dscores
        p_scores /= p_scores.sum()

        new_deepscore: DeepScore = RNG.choice(scores, p=p_scores)
        # TODO: fix this for depth > 1
        paths = [self.edges[w][2] for w in new_deepscore.words]
        return new_deepscore.words, paths, new_deepscore.nodes

    def _to_ascii(self) -> Iterator[str]:
        yield f"State: {self.state.to_binary()}, Last Letter: {self.state.flat_letters[self.last_index]}"
        yield "Edges"
        for e_word, (e_score, e_game, e_path) in sorted(self.edges.items()):
            yield f"    {e_word.ljust(15)} -> {str(e_score).ljust(5)} ({e_game.state.to_binary()})"
        yield ""

    def to_ascii(self) -> str:
        """Render this node in a way that promotes debugging"""
        return "\n".join(self._to_ascii())


@define
class Trajectory:
    words: List[str] = field(factory=list)
    paths: List[List[int]] = field(factory=list)
    states: List[Game] = field(factory=list)

    def add_words_states(
        self, words: List[str], paths: List[List[int]], states: List[Game]
    ):
        self.words.extend(words)
        self.paths.extend(paths)
        self.states.extend(states)

    def is_fail(self) -> bool:
        return len(self.states) == 0 or not self.states[-1].is_win()
