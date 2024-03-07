"""Various helper methods that are independent of the solve algorithm"""

from typing import List, Any, Dict, Set, Optional, Iterator, Tuple, Generic, TypeVar
import string
import re

from attrs import define, field
import numpy as np

from .words import WORDS

RNG = np.random.default_rng(seed=69420)
"""A random number generator used to establish a global seed"""


@define
class ValidLiterals:
    """A class to hold all valid literals (words) from a source file"""

    words: Set[str] = field()
    words_by_letter: Dict[str, Set[str]] = field()

    @classmethod
    def build(cls) -> "ValidLiterals":
        words = set(
            x.lower()
            for letter_words in WORDS
            for x in sorted(letter_words.keys())
            if re.match(r"^[a-zA-Z]+$", x)
        )

        words_by_letter: Dict[str, Set[str]] = dict()
        for w in words:
            words_w_letter = words_by_letter.setdefault(w[0], set())
            words_w_letter.add(w)
        return cls(words, words_by_letter)


def build_letters(S: int) -> List[str]:
    letter_frequencies = np.array(
        [
            0.0817,  # A
            0.0149,  # B
            0.0278,  # C
            0.0425,  # D
            0.127,  # E
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
            0.0007,  # Z
        ]
    )
    letter_frequencies /= letter_frequencies.sum()
    letters = [c for c in string.ascii_lowercase]
    return np.random.choice(
        letters, p=letter_frequencies, size=S * 4, replace=True
    ).tolist()


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


IteratorVal = TypeVar("IteratorVal")


@define()
class CircularIterator(Generic[IteratorVal]):
    """A thin wrapper for an Iterator that cycles over an iterator,
    while caching seen value
    """

    iterator: Iterator[IteratorVal] = field()
    _current_index: int = field(default=0)
    _num_yielded: int = field(default=0)
    _empty: bool = field(default=False)

    _cache: List[IteratorVal] = field(factory=list)
    _cache_len: int = field(default=0)

    def __hash__(self):
        return id(self.iterator)

    def _get_value_at_index(self, index: int) -> Optional[IteratorVal]:
        index = (
            self._current_index
            if not self._empty or self._cache_len == 0
            else self._current_index % self._cache_len
        )
        if index < self._cache_len:
            # We're looking for a value we've already computed
            return self._cache[index]

        # We need to compute our way from the current _cache_len
        # to the requested value
        for i in range(self._cache_len, index + 1):
            try:
                val = next(self.iterator)
                self._cache.append(val)
                self._cache_len += 1
                return val
            except StopIteration:
                self._empty = True
                return None
        return None

    def __next__(self):
        val = self._get_value_at_index(self._current_index)
        if val is None:
            # We didn't find out we were empty until here, try to cycle back
            # (we might get nothing)
            val = self._get_value_at_index(self._current_index)
            if val is None:
                raise StopIteration

        self._current_index += 1
        return val

    def __iter__(self):
        # Count the number of values we've hit
        counter = 0
        # Iterate if we are not empty yet OR
        # we have yet to emit all of the values in our cache
        while not self._empty or counter != self._cache_len:
            # Query the next value
            value = self._get_value_at_index(self._current_index)

            # Exit the loop if we're empty and we've emitted all of
            # the values from the iterator
            if self._empty and counter == self._cache_len:
                return

            # If it's None, that means we hit the end of the iterator, but
            # we didn't know that we were at the end yet to perform modular
            # indexing.
            # We should never yield a None, so we should cycle back by
            # trying again
            if value is None:
                value = self._get_value_at_index(self._current_index)

            # Successful yield
            counter += 1
            self._current_index += 1
            yield value

    def peek(self) -> Optional[Tuple[IteratorVal, Iterator[IteratorVal]]]:
        """Peek inside a generator

        Returns
        -------
        Tuple[IteratorVal, CircularIterator[IteratorVal]], optional
            The first value, and the remaining iterator, starting at
            the next value
        """
        try:
            first = next(self)
        except StopIteration:
            return None

        return first, self


def can_make_word(
    w: str, letters: Dict[str, Set[int]], S: int, trajectory: Optional[List[int]] = None
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
        yield from can_make_word(w_else, letters, S, trajectory=trajectory + [next_loc])
