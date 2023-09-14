"""Various helper methods that are independent of the solve algorithm"""

from typing import List, Any, Dict, Set, Optional, Iterator
import string
import json
import re

from attrs import define, field
import numpy as np

RNG = np.random.default_rng(seed=69420)
"""A random number generator used to establish a global seed"""


@define
class ValidLiterals:
    """A class to hold all valid literals (words) from a source file"""

    words: Set[str] = field()
    words_by_letter: Dict[str, Set[str]] = field()

    @classmethod
    def build(cls, path_to_source: str) -> "ValidLiterals":

        with open(path_to_source, "r") as f:
            words = set(x.lower() for letter_words in json.load(f) for x in sorted(letter_words.keys()) if re.match(r'^[a-zA-Z]+$', x))

            words_by_letter: Dict[str, Set[str]] = dict()
            for w in words:
                words_w_letter = words_by_letter.setdefault(w[0], set())
                words_w_letter.add(w)
        return cls(words, words_by_letter)


def build_letters(S: int) -> List[str]:

    letter_frequencies = np.array([
        0.0817,  # A
        0.0149,  # B
        0.0278,  # C
        0.0425,  # D
        0.127,   # E
        0.0223,  # F
        0.0202,  # G
        0.0609,  # H
        0.0697,  # I
        0.0015,  # J
        0.0077,  # K
        0.0403,  # L
        0.0241,  # M
        0.0675,  # N
        0.0751,  # O
        0.0193,  # P
        0.0010,  # Q
        0.0599,  # R
        0.0633,  # S
        0.0906,  # T
        0.0276,  # U
        0.0098,  # V
        0.0236,  # W
        0.0015,  # X
        0.0197,  # Y
        0.0007   # Z
    ])
    letter_frequencies /= letter_frequencies.sum()
    letters = [c for c in string.ascii_lowercase]
    return np.random.choice(letters, p=letter_frequencies, size=S * 4, replace=True).tolist()

# def build_letters(S: int) -> List[str]:

#     # To mimic the distribution of vowels within the english
#     # language, just sample random words until we meet the
#     # total number of letters required, and shuffle them
#     s = ""
#     c = 0
#     l_words = list(WORDS)
#     while c < S * 4:
#         word = RNG.choice(l_words)
#         s += word
#         c += len(word)
#     return RNG.permutation([char for char in s[:S * 4]]).tolist()


def state_factory(s: int, fill: Any) -> List[Any]:
    # Four sides, each of length s
    return [fill] * s * 4


def can_make_word(
    w: str,
    letters: Dict[str, Set[int]],
    S: int,
    trajectory: Optional[List[int]] = None
) -> Iterator[List[int]]:

    # Success case
    if w == "" and trajectory is not None:
        yield trajectory
        return

    # Dissect the word into first char and suffix
    w_0, w_else = w[0], w[1:]

    # Immediately discard if the letter isn't in the game
    if (next_locs := letters.get(w_0)) is None:
        return

    # Entry case: no trajectory yet
    if trajectory is None:
        trajectory = []

    for next_loc in next_locs:

        # Failure case: we are on the same side
        cur_loc = trajectory[-1] if trajectory else -1
        if cur_loc // S == next_loc // S:
            continue

        # Recursively try each possible next loc
        yield from can_make_word(
            w_else, letters, S, trajectory=trajectory + [next_loc]
        )
