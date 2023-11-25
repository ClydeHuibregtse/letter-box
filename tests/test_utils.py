
import pytest
from letter_box.utils import (
    ValidLiterals,
    CircularIterator,
    can_make_word
)


def test_literals():
    """Tests implementation of ValidLiterals"""

    vl = ValidLiterals.build()

    print(f"Total number of literals in the source: {len(vl.words)}")
    print(f"Total number of starting letters in the source: {len(vl.words_by_letter)}")
    for letter, words in sorted(vl.words_by_letter.items()):
        print(f"    Number of literals starting with {letter}: {len(words)}")


def test_can_make_word():
    """Correctness: can_make_word"""

    # Here we condense the following game into its
    # index datastructure
    # --------------------------------
    #    U I G
    #  M       A
    #  A       A
    #  I       N
    #    P B G
    # --------------------------------
    S = 3
    letters = {
        'u': {0},
        'i': {1, 9},
        'g': {2, 6},
        'a': {10, 3, 4},
        'n': {5},
        'b': {7},
        'p': {8},
        'm': {11}
    }
    # These are valid words
    assert list(can_make_word("map", letters, S)) == [
        [11, 3, 8],
        [11, 4, 8]
    ]
    assert list(can_make_word("magi", letters, S)) == [
        [11, 3, 2, 9],
        [11, 3, 6, 1],
        [11, 3, 6, 9],
        [11, 4, 2, 9],
        [11, 4, 6, 1],
        [11, 4, 6, 9]
    ]
    assert list(can_make_word("paan", letters, S)) == [
        [8, 3, 10, 5],
        [8, 4, 10, 5]
    ]
    assert list(can_make_word("panini", letters, S)) == [
        [8, 10, 5, 1, 5, 1],
        [8, 10, 5, 1, 5, 9],
        [8, 10, 5, 9, 5, 1],
        [8, 10, 5, 9, 5, 9]
    ]
    assert list(can_make_word("gaining", letters, S)) == [
        [2, 10, 1, 5, 1, 5, 2], [2, 10, 1, 5, 1, 5, 6],
        [2, 10, 1, 5, 9, 5, 2], [2, 10, 1, 5, 9, 5, 6],
        [2, 3, 1, 5, 1, 5, 2], [2, 3, 1, 5, 1, 5, 6],
        [2, 3, 1, 5, 9, 5, 2], [2, 3, 1, 5, 9, 5, 6],
        [2, 3, 9, 5, 1, 5, 2], [2, 3, 9, 5, 1, 5, 6],
        [2, 3, 9, 5, 9, 5, 2], [2, 3, 9, 5, 9, 5, 6],
        [2, 4, 1, 5, 1, 5, 2], [2, 4, 1, 5, 1, 5, 6],
        [2, 4, 1, 5, 9, 5, 2], [2, 4, 1, 5, 9, 5, 6],
        [2, 4, 9, 5, 1, 5, 2], [2, 4, 9, 5, 1, 5, 6],
        [2, 4, 9, 5, 9, 5, 2], [2, 4, 9, 5, 9, 5, 6],
        [6, 10, 1, 5, 1, 5, 2], [6, 10, 1, 5, 1, 5, 6],
        [6, 10, 1, 5, 9, 5, 2], [6, 10, 1, 5, 9, 5, 6],
        [6, 3, 1, 5, 1, 5, 2], [6, 3, 1, 5, 1, 5, 6],
        [6, 3, 1, 5, 9, 5, 2], [6, 3, 1, 5, 9, 5, 6],
        [6, 3, 9, 5, 1, 5, 2], [6, 3, 9, 5, 1, 5, 6],
        [6, 3, 9, 5, 9, 5, 2], [6, 3, 9, 5, 9, 5, 6],
        [6, 4, 1, 5, 1, 5, 2], [6, 4, 1, 5, 1, 5, 6],
        [6, 4, 1, 5, 9, 5, 2], [6, 4, 1, 5, 9, 5, 6],
        [6, 4, 9, 5, 1, 5, 2], [6, 4, 9, 5, 1, 5, 6],
        [6, 4, 9, 5, 9, 5, 2], [6, 4, 9, 5, 9, 5, 6]
    ]
    # These are not
    assert list(can_make_word("maam", letters, S)) == []
    assert list(can_make_word("asdf", letters, S)) == []

    # Make sure this works with a different number of dimensions
    S = 2
    # --------------------------------
    #    U G
    #  M     A
    #  I     N
    #    P G
    # --------------------------------
    letters = {
        "u": {0},
        "g": {1, 4},
        "a": {2},
        "n": {3},
        "p": {5},
        "i": {6},
        "m": {7}
    }
    # These are valid words
    assert list(can_make_word("magi", letters, S)) == [
        [7, 2, 1, 6],
        [7, 2, 4, 6]
    ]
    assert list(can_make_word("pig", letters, S)) == [
        [5, 6, 1],
        [5, 6, 4]
    ]
    assert list(can_make_word("gum", letters, S)) == [[4, 0, 7]]
    # These are not
    assert list(can_make_word("asdf", letters, S)) == []


def test_restart_iterator():

    # Build an iterator
    iterator = CircularIterator(x for x in range(10))

    # Check the iterator's contents
    assert list(iterator) == list(range(10))

    # The cache should be populated
    assert iterator._cache == list(range(10))

    # Now again
    assert list(iterator) == list(range(10))

    # If we "next" twice, we should be starting at index 2
    iterator = CircularIterator(x for x in range(10))

    assert next(iterator) == 0
    assert next(iterator) == 1
    assert iterator._current_index % 10 == 2
    assert list(iterator) == [2, 3, 4, 5, 6, 7, 8, 9, 0, 1]
    assert list(iterator) == [2, 3, 4, 5, 6, 7, 8, 9, 0, 1]

    # Try on a fresh iterator to manually next through a cycle
    iterator = CircularIterator(x for x in range(5))
    assert next(iterator) == 0
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert next(iterator) == 3
    assert next(iterator) == 4
    assert next(iterator) == 0
    assert next(iterator) == 1
    # Now iterate
    assert list(iterator) == [2, 3, 4, 0, 1]

    # Check if something is inside the new iterator
    iterator = CircularIterator(x for x in range(10))
    # Peek once
    peek_val = iterator.peek()
    assert peek_val is not None
    assert iterator._current_index == 1
    assert iterator._cache_len == 1
    # Do another next
    assert next(iterator) == 1
    assert iterator._current_index == 2
    assert iterator._cache_len == 2
    # Peek again
    peek_val = iterator.peek()
    assert iterator._current_index == 3
    assert iterator._cache_len == 3

    # We should have a value, and it should be the 2nd index value,
    # since we did "next" twice above
    assert peek_val is not None
    first, remaining_iterator = peek_val
    assert first == iterator._cache[2]
    # and the iterator is the same object
    assert iterator is remaining_iterator

    assert list(remaining_iterator) == [3, 4, 5, 6, 7, 8, 9, 0, 1, 2]
    assert list(iterator) == [3, 4, 5, 6, 7, 8, 9, 0, 1, 2]

    # If we peek again, we should get the next value, but the iterator
    # should still start from 0
    peek_val = iterator.peek()
    assert peek_val is not None
    first, remaining_iterator = peek_val
    assert first == iterator._cache[3]
    assert list(remaining_iterator) == [4, 5, 6, 7, 8, 9, 0, 1, 2, 3]

    for _ in range(1000):
        assert len(list(iterator)) == 10

    # Try an empty iterator
    empty = CircularIterator(x for x in [])
    with pytest.raises(StopIteration):
        next(empty)

    list(empty) == []


if __name__ == "__main__":
    test_restart_iterator()
