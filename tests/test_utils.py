import os
from letter_box.utils import (
    ValidLiterals,
    RestartIterator,
    can_make_word
)


def test_literals():
    """Tests implementation of ValidLiterals"""

    vl = ValidLiterals.build(os.path.join(os.path.dirname(__file__), "..", "letter_box", "words.json"))

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

    # Build and iterator
    iterator = RestartIterator(x for x in range(10))
    # for val in iterator:
    #     print(val)

    for _ in range(1000000):
        assert len(list(iterator)) == 10


    iterator.get_value_at_index(0)
    iterator.get_value_at_index(0)
    iterator.get_value_at_index(1)

    # Check that it's iterable, and doesn't empty as it iterates
    # assert len(list(iterator)) == 10
    # assert len(list(iterator)) == 10


if __name__ == "__main__":
    test_restart_iterator()
