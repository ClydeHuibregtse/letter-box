
import pytest
import string
import time
from letter_box.utils import (
    can_make_word,
    build_letters,
    RNG
)
from letter_box.games import Game


@pytest.mark.skip()
def test_can_make_word_profile():
    """Profile: can_make_word"""

    # Experiment with the algorithmic runtime of can_make_word's
    # performance w.r.t the various parameters
    lc_letters = [x for x in string.ascii_lowercase]

    def sample_word(lc_letters, L):
        return "".join(RNG.choice(lc_letters, size=L))

    def build_and_sample(S: int, L: int):
        N_games = 2
        N_words = 5
        total = 0.0
        for _ in range(N_games):
            letters = build_letters(S)
            game = Game.new(letters)
            for _ in range(N_words):
                word = sample_word(lc_letters, L)
                now = time.time()
                can_make_word(word, game.letters, S)
                total += time.time() - now

        return total / (N_games * N_words)

    import pandas as pd
    import seaborn as sns
    df = pd.DataFrame(columns=["S", "L", "can_make_word_time"])

    for S in range(1, 51, 5):
        for L in range(1, 51, 5):
            check_time = build_and_sample(S, L)
            print(S, L, check_time)
            df.loc[len(df)] = [S, L, check_time]

    print(df)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 10))
    # pos = ax.imshow(
    #     df.pivot(index='S', columns='L', values='can_make_word_time'),
    #     interpolation="nearest",
    #     )
    # fig.colorbar(pos, ax=ax)

    sns.heatmap(
        df.pivot(index='S', columns='L', values='can_make_word_time'),
        cmap="coolwarm",
        cbar=True,
    )
    plt.show()


def test_can_make_word_double_letter():

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
    #   3. [15, 5, 2, 11] # e's on the first and second edge (reversed 1 - ignore)
    #   4. [15, 6, 2, 11] # e's on the first and second edge (reversed 2 - ignore)
    # We have to be able to coerce both sets of these
    letters = [
        "h", "q", "e", "o", "d", "e", "e", "a",
        "o", "a", "h", "n", "f", "g", "c", "t"
    ]

    game = Game.new(letters)

    assert can_make_word("teen", game.letters, game.S) == [
        [15, 2, 5, 11],
        [15, 2, 6, 11],
        [15, 5, 2, 11],
        [15, 6, 2, 11]
    ]
