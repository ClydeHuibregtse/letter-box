"""Abstractions for the state of a letter-box game"""
from attrs import define, field
from typing import List, Dict, Set

import numpy as np

from .utils import (
    state_factory
)


@define
class Game(object):

    letters: Dict[str, Set[int]] = field()
    state: List[bool] = field()
    S: int = field()
    flat_letters: List[str] = field()

    @classmethod
    def new(cls, letters: List[str]) -> "Game":
        S = len(letters) // 4
        mapped_letters: Dict[str, Set[int]] = dict()
        for i, l in enumerate(letters):
            if l in mapped_letters:
                mapped_letters[l].add(i)
            else:
                mapped_letters[l] = {i}
        return Game(mapped_letters, state_factory(S, False), S, letters)

    def __repr__(self) -> str:
        return self.to_binary()

    def to_ascii(self) -> str:
        """Render this game state in ascii characters for ease-of-debugging"""

        # Build a "table"-like array into which we populate ascii characters
        # Joining these with \n and spaces will emit a board
        S = len(self.state) // 4  # always an integer
        board = np.empty((S + 4, S + 4), dtype=str)

        # Draw letters
        for letter, locs in self.letters.items():

            for loc in locs:
                # Determine where on the board the letter lies
                side = loc // S
                index_along_side = loc - side * S

                # If the letter is filled, let's put a * next to it
                filled_char = "*" if self.state[loc] else ""

                if side == 0:
                    # Top
                    board[0, index_along_side + 2] = letter
                    board[1, index_along_side + 2] = filled_char

                elif side == 1:
                    # Right
                    board[index_along_side + 2, -1] = letter
                    board[index_along_side + 2, -2] = filled_char

                elif side == 2:
                    # Bottom
                    board[-1, S + 3 - (index_along_side + 2)] = letter
                    board[-2, S + 3 - (index_along_side + 2)] = filled_char

                else:
                    # Left
                    board[S + 3 - (index_along_side + 2), 0] = letter
                    board[S + 3 - (index_along_side + 2), 1] = filled_char

        return "\n" + "\n".join("".join(char.ljust(5) for char in board[r, :]) for r in range(board.shape[0])) + "\n"

    def to_binary(self) -> str:
        return "".join("1" if x else "0" for x in self.state)

    def update_state(self, state: List[bool]) -> "Game":
        """Ingest a new state and emit a new Game object with the new state"""
        return Game(
            self.letters, state, self.S, self.flat_letters
        )

    def is_win(self) -> bool:
        return all(self.state)

    def score(self) -> int:
        return sum(self.state)
