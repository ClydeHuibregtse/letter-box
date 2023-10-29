import os
from typing import Dict, List, Tuple, Set, Optional, Iterator, Any
import itertools

from attrs import define, field

from .games import Game
from .utils import (
    can_make_word,
    RestartIterator,
    ValidLiterals
)

VALID_LITERALS = ValidLiterals.build(os.path.join(os.path.dirname(__file__), "words.json"))


@define
class Oracle(object):

    game: Game = field()
    _word_mapping: Dict[int, Set[str]] = field(factory=dict)
    _word_path_mapping: Dict[Tuple[int, str], RestartIterator] = field(factory=dict)

    @classmethod
    def new(cls, letters: List[str]) -> "Oracle":

        # Build the barren game from the
        # provided letters
        game = Game.new(letters)

        return Oracle(game)

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
        self._word_mapping[start_index] = self._build_valid_words_cache(
            start_index
        )
        return self._word_mapping[start_index]

    def _build_valid_words_cache(self, start_index: int) -> Set[str]:
        """Build a cache of valid words beginning at start_index"""
        start_letter = self.game.flat_letters[start_index]
        candidate_words = VALID_LITERALS.words_by_letter[start_letter]

        valid_words = set()
        for w in candidate_words:
            valid_paths = RestartIterator(
                can_make_word(
                    w[1:], self.game.letters, self.game.S, trajectory=[start_index]
                )
            )
            if (
                start_index in self.game.letters[w[0]]       # First char is in right location
                and valid_paths.peek() is not None           # Remainder is valid
            ):
                # Extend the cache
                if (start_index, w) not in self._word_path_mapping:
                    self._word_path_mapping[(start_index, w)] = valid_paths
                # self._word_path_mapping[(start_index, w)].extend(valid_paths)
                valid_words.add(w)

        return valid_words

    def valid_paths_by_word(self, w: str, start_index: int) -> Iterator[List[int]]:
        yield from self._word_path_mapping[(start_index, w)]

    def submit_word(
        self,
        game: Game,
        w: str,
        start_index: int
    ) -> Optional[Tuple[Game, List[int]]]:
        """Submit a word and return a new Game and the path used to get there"""
        # Get all valid paths for this word (may hit cache)
        paths = self.valid_paths_by_word(w, start_index)

        # Iterate over all paths, and accept the first one that adds
        # any score
        best_path = []
        for path in paths:
            best_path = path
            if sum(not game.state[i] for i in path) > 0:
                break
        # If no best path, then we have no valid paths
        if len(best_path) == 0:
            return None

        new_state = game.state[:]
        for idx in best_path:
            new_state[idx] = True

        new_game = game.update_state(new_state)
        return new_game, best_path
