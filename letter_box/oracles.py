from typing import Dict, List, Tuple, Set, Optional, Iterator, TYPE_CHECKING
import pandas as pd
from attrs import define, field

from .games import Game
from .utils import can_make_word, CircularIterator, ValidLiterals

if TYPE_CHECKING:
    from .graphs import GraphNode

VALID_LITERALS = ValidLiterals.build()


@define
class Oracle(object):
    game: Game = field()
    _word_mapping: Dict[int, Set[str]] = field(factory=dict)
    _word_path_mapping: Dict[Tuple[int, str], CircularIterator] = field(factory=dict)
    _graph_nodes: Dict[Tuple[int, int], "GraphNode"] = field(factory=dict)

    @classmethod
    def new(cls, letters: List[str]) -> "Oracle":
        # Build the barren game from the
        # provided letters
        game = Game.new(letters)

        return Oracle(game)

    def get_graph_node(self, state: int, letter_index: int) -> Optional["GraphNode"]:
        """Look up the node in our graph, if we have it"""
        return self._graph_nodes.get((state, letter_index))

    def set_graph_node(self, state: int, letter_index: int, node: "GraphNode"):
        """Store a graph node in the cache"""
        self._graph_nodes[(state, letter_index)] = node

    def graph_nodes_to_dfs(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Emit both nodes and edges dataframes"""
        # nodes = [0, self.game.to_binary(), self.game.state, s]
        nodes = list()
        edges = list()
        for graph_node in self._graph_nodes.values():
            nodes.append(
                (
                    id(graph_node),
                    graph_node.state.to_binary(),
                    graph_node.state.state,
                    graph_node.last_index,
                    graph_node.state.score(),
                )
            )
            for w, (s, e, p) in graph_node.edges.items():
                edges.append((id(graph_node), id(e), w, s + 1))

        node_df = pd.DataFrame.from_records(
            nodes, columns=["id", "Label", "state", "index", "score"]
        )
        edge_df = pd.DataFrame.from_records(
            edges, columns=["Source", "Target", "Label", "Weight"]
        )
        return node_df, edge_df

    def valid_words_by_letter(self, start_index: int) -> Set[str]:
        """Return all valid words that begin at some index"""

        # If we hit the cache, return the cached set
        # Possible memory leak for large games
        # Consider:
        #   - a more intelligent heap of words indexed by length,
        #     word diversity, etc.
        if start_index in self._word_mapping:
            return self._word_mapping[start_index]

        # Otherwise, compute the valid words cache
        self._word_mapping[start_index] = self._build_valid_words_cache(start_index)
        return self._word_mapping[start_index]

    def _build_valid_words_cache(self, start_index: int) -> Set[str]:
        """Build a cache of valid words beginning at start_index"""
        start_letter = self.game.flat_letters[start_index]
        candidate_words = VALID_LITERALS.words_by_letter[start_letter]

        valid_words = set()
        for w in candidate_words:
            # Wrap the result of our can_make_word generator in a
            # wrapper that makes it cached and circular, so we can
            # cheaply query from it over and over, if the same word is tried
            # many times, and the generator doesn't run out, accidentally
            # nixing words from the vocabulary
            valid_paths = CircularIterator(
                can_make_word(
                    w[1:], self.game.letters, self.game.S, trajectory=[start_index]
                )
            )
            if (
                start_index
                in self.game.letters[w[0]]  # First char is in right location
                and valid_paths.peek() is not None  # Remainder is valid
            ):
                # Extend the cache
                if (start_index, w) not in self._word_path_mapping:
                    self._word_path_mapping[(start_index, w)] = valid_paths
                valid_words.add(w)

        return valid_words

    def valid_paths_by_word(self, w: str, start_index: int) -> Iterator[List[int]]:
        return self._word_path_mapping[(start_index, w)]

    @staticmethod
    def or_integer_with_indices(num: int, indices: List[int]):
        """Compute logical OR between a float (num)
        and a list of bits of a number = 1
        """
        result = num
        for index in indices:
            result |= 1 << index
        return result

    def submit_word(
        self, game: Game, w: str, start_index: int
    ) -> Optional[Tuple[Game, List[int]]]:
        """Submit a word and return a new Game and the path used to get there"""
        # Get all valid paths for this word (may hit cache)
        paths = self.valid_paths_by_word(w, start_index)

        # Iterate over all paths, and accept the first one that adds
        # any score
        best_path = []
        for path in paths:
            best_path = path
            if (
                new_state := self.or_integer_with_indices(game.state, path)
            ) > game.state:
                break

        # If no best path, then we have no valid paths
        if len(best_path) == 0:
            return None

        new_game = game.update_state(new_state)
        return new_game, best_path
