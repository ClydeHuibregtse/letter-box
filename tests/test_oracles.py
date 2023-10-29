
from letter_box.oracles import Oracle


def test_word_caching():
    """Tests that words are being cached properly by the Oracle"""
    # Example Game
    # -----------------------
    #     h    q    e    o
    # t                     d
    # c                     e
    # g                     e
    # f                     a
    #     n    h    a    o
    # -----------------------
    # The word "teen" is a valid word on this graph
    # Solution paths are:
    #   1. [15, 2, 5, 11] # e's on the first and second edge
    #   2. [15, 2, 6, 11] # e's on the first and second edge (other e)
    #   3. [15, 5, 2, 11] # e's on the first and second edge (reversed 1)
    #   4. [15, 6, 2, 11] # e's on the first and second edge (reversed 2)
    # We have to be able to coerce both sets of these
    letters = [
        "h", "q", "e", "o", "d", "e", "e", "a",
        "o", "a", "h", "n", "f", "g", "c", "t"
    ]

    oracle = Oracle.new(letters)
    t_words = oracle.valid_words_by_letter(15)

    assert len(t_words) == len(oracle._word_path_mapping)

    # (15, "teen") is a valid word in our mapping
    t_paths = oracle._word_path_mapping[(15, "teen")]
    assert list(t_paths) == [
        # Note these are one out of cycle because "peek" is called once internally
        [15, 2, 6, 11],
        [15, 5, 2, 11],
        [15, 6, 2, 11],
        [15, 2, 5, 11],
    ]

    # It should remain hydrated
    assert list(t_paths) == [
        [15, 2, 6, 11],
        [15, 5, 2, 11],
        [15, 6, 2, 11],
        [15, 2, 5, 11],
    ]

    teen_paths = oracle.valid_paths_by_word("teen", 15)
    assert teen_paths is t_paths
