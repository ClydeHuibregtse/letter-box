"""Profile the performance of various encodings of the game 'state' """
from typing import List
import numpy as np
import os


def random_path(N: int) -> List[int]:
    """Return a random permutation of the numbers from 1,...,N"""
    return np.random.permutation(N).tolist()


def boolean_state(N: int) -> List[bool]:
    """Return a list of booleans describing the current state

    (original implementation of this bot used this)
    """
    return np.random.choice([True, False], size=N).tolist()


def integer_state(N: int) -> int:
    """Return an integer whose binary representation is
    the current state
    """
    # return np.random.randint(0, 2 ** N)
    return 2 ** N


def iterative_compare(state: List[bool], path: List[int]) -> bool:
    """Iterates over all indices in path and asks if flipping
    the corresponding bits would result in an increase in the
    score of the state
    """
    return sum(not state[i] for i in path) > 0


def integer_compare_expand_state(state: int, path: List[int]) -> bool:
    """Uses binary arithmetic to determine if the path increases
    the score of the state"""
    path_state = sum(2 ** n for n in path)
    return (state | path_state) > state


def or_integer_with_indices(num: int, indices: List[int]):
    """Compute logical OR between a float (num)
    and a list of bits of a number = 1
    """
    result = num
    for index in indices:
        result |= (1 << index)
    return result


def integer_compare_binary_state(state: int, path: List[int]) -> bool:
    """Uses binary arithmetic to determine if the path increases
    the score of the state"""
    return or_integer_with_indices(state, path) > state


def profile():

    import timeit
    from pandas import DataFrame
    from matplotlib import pyplot as plt

    N_MAX = 1024
    path_data = []
    score_data = []
    for N in range(N_MAX):
        print(N)
        path = random_path(N)
        bool_state = boolean_state(N)
        int_state = integer_state(N)

        score_data.append({
            "N": N,
            "Iterative Score": timeit.timeit(lambda: sum(bool_state), number=100),
            "Integer Score": timeit.timeit(lambda: int_state.bit_count(), number=100),
        })
        path_data.append({
            "N": N,
            "Iterative Compare": timeit.timeit(lambda: iterative_compare(bool_state, path), number=100),
            "Integer Compare (exp)": timeit.timeit(lambda: integer_compare_expand_state(int_state, path), number=100),
            "Integer Compare (bin)": timeit.timeit(lambda: integer_compare_binary_state(int_state, path), number=100)
        })

    path_df = DataFrame.from_records(path_data, index="N")
    score_df = DataFrame.from_records(score_data, index="N")

    path_df.plot()
    plt.savefig(os.path.join(os.path.dirname(__file__), "profiles", "path_times.png"))

    score_df.plot()
    plt.savefig(os.path.join(os.path.dirname(__file__), "profiles", "score_times.png"))


if __name__ == "__main__":
    profile()
