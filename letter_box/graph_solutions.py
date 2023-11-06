"""Various classes to support the implementation of the shortest path
graph algorithm"""
from typing import List, Dict, Tuple, Optional, Iterator

from attrs import define, field
import numpy as np

from .games import Game
from .oracles import Oracle
from .utils import RNG


@define
class DeepScore():
    words: List[str] = field()
    score: float = field()
    nodes: List["GraphNode"] = field()


@define
class GraphNode():

    state: Game = field()
    # Consider what happens when two divergent trajectories return to a shared state with
    # a different "last_index" - I suspect this is not likely nor impactful to performance
    last_index: int = field()
    oracle: Oracle = field()
    edges: Dict[str, Tuple[float, "GraphNode", List[int]]] = field(factory=dict)

    @classmethod
    def new(
        cls,
        game: Game,
        last_index: int,
        oracle: Optional[Oracle] = None
    ) -> "GraphNode":
        oracle = oracle or Oracle(game)
        return GraphNode(
            game, last_index, oracle
        )

    def find_edges(self, depth_of_search: int = 1):

        # Once we've run out of layers, exit
        if depth_of_search == 0:
            return

        # Populate the edges that are pointed away from this node
        if len(self.edges) == 0:
            S = len(self.state.flat_letters) // 4
            self.edges = GraphNode.compute_edges(self, self.last_index, S)

        # Recurse depending on depth
        for w, (s, e_node, e_path) in self.edges.items():
            e_node.find_edges(depth_of_search=depth_of_search - 1)

    @staticmethod
    def compute_edges(node: "GraphNode", last_index: int, S: int) -> Dict[str, Tuple[float, "GraphNode", List[int]]]:

        edges = dict()
        for word in node.oracle.valid_words_by_letter(last_index):

            if (res := node.oracle.submit_word(node.state, word, last_index)) is None:
                continue
            next_state, path = res
            next_node = GraphNode.new(
                next_state, path[-1], oracle=node.oracle
            )
            edges[word] = (
                GraphNode.transition_score(node, next_node),
                next_node,
                path
            )
        return edges

    def compute_scores(self, depth_of_search: int = 1) -> List["DeepScore"]:

        scores = []
        for w, (s, e, p) in self.edges.items():

            # First, recurse and get all scores from the subtree
            subgraph_scores = e.compute_scores()

            # If no subgraph exists, just add this score
            if len(subgraph_scores) == 0 or depth_of_search == 1:
                scores.append(
                    DeepScore([w], s, [e])
                )

            # Otherwise, add the edge data to the scores
            else:
                for sg_score in subgraph_scores:
                    scores.append(
                        DeepScore(
                            [w] + sg_score.words, s + sg_score.score, [e] + sg_score.nodes
                        )
                    )

        return scores

    @staticmethod
    def transition_score(n1: "GraphNode", n2: "GraphNode") -> float:
        """Return the score associated with transitioning from n1 to n2"""
        # Trajectories leave a scent that is the inverse of the the number of words it took to get there
        return float(n2.state.score() - n1.state.score())

    def visit(
        self,
        T: float,
        depth_of_search: int = 1
    ) -> Optional[Tuple[List[str], List[List[int]], List["GraphNode"]]]:

        if self.state.is_win():
            return None

        # Compute the edges out of this node, if they haven't
        # already been found
        self.find_edges(depth_of_search=depth_of_search)
        # Compute the depth_of_search score for each leaf node
        scores = np.array(self.compute_scores())

        # Select an edge probabilistically
        p_scores = np.array([s.score ** 10 for s in scores])

        # Add variance to the scores until we've refined our temperature
        sum_scores = p_scores.sum()
        if sum_scores == 0:
            return None
        p_scores /= sum_scores
        dscores = np.clip(RNG.random(len(p_scores)) * T, 0, 10)
        p_scores += dscores
        p_scores /= p_scores.sum()

        new_deepscore: DeepScore = RNG.choice(scores, p=p_scores)
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
class Trajectory():

    words: List[str] = field(factory=list)
    paths: List[List[int]] = field(factory=list)
    states: List[Game] = field(factory=list)

    def add_words_states(self, words: List[str], paths: List[List[int]], states: List[Game]):
        self.words.extend(words)
        self.paths.extend(paths)
        self.states.extend(states)

    def is_fail(self) -> bool:
        return len(self.states) == 0 or not self.states[-1].is_win()
