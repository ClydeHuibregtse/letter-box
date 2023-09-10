
from attrs import field, define
from typing import List, Any, Dict, Set, Optional

from copy import deepcopy
import random
import string


import re
with open("/usr/share/dict/words", "r") as f:
    WORDS = set(x.lower() for x in re.sub("[^\w]", " ",  f.read()).split())

N = 3
"""Number of letters per side of the square"""

def is_english_word(w: str) -> bool:
    return w in WORDS

def state_factory(s: int, fill: Any) -> List[Any]:
    # Four sides, each of length s
    return [fill] * s * 4

def letters_factory(s: int) -> List[str]:
    letters = set()
    for _ in range(s * 4):
        while True:
            if (char := random.choice(string.ascii_lowercase)) not in letters:
                letters.add(char)
                break

    return list(letters)

def can_make_word(w: str, letters: List[str]) -> bool:
    s = len(letters) // 4
    prev_loc: int = -1
    for char in w:
        try:
            loc = letters.index(char)
            if loc // s == prev_loc // s:
                # Letter on same side of square
                return False
            prev_loc = loc
        except ValueError:
            # Letter not found
            return False
    return True

def find_valid_words(letters: List[str], start_letter: str) -> Set[str]:

    valid_words = set()

    # Number of letters per side
    N = len(letters) / 4
    for w in WORDS:
        if not w.startswith(start_letter):
            continue
        # Letterboxed unique length-3 requirement
        if can_make_word(w, letters) and len(w) > 3:
            valid_words.add(w)
    return valid_words


@define
class Game(object):

    letters: List[int] = field(factory=lambda: letters_factory(N))
    state: List[bool] = field(factory=lambda: state_factory(N, False))

    def submit_word(self, w: str) -> "Game":
        """Submit a word and return a new Game"""

        new_state = deepcopy(self.state)
        if not is_english_word(w):
            raise Exception(f"Not a word: {w}")
        for char in w:
            loc = self.letters.index(char)
            new_state[loc] = True

        return Game(self.letters, new_state)

    def is_win(self) -> bool:
        return all(self.state)
    
    def score(self) -> int:
        return sum(self.state)
    

@define
class GraphNode(object):

    state: Game = field()
    graph: Dict[str, "GraphNode"] = field(factory=dict)

    def build_subgraph(self, last_word: Optional[str] = None):
        if self.state.is_win():
            return

        if last_word is None:
            start_letter = ""
        else:
            start_letter = last_word[-1]
        valid_words = find_valid_words(self.state.letters, start_letter)

        graph: Dict[str, GraphNode] = dict()
        for w in valid_words:
            new_game_state = self.state.submit_word(w)
            if new_game_state.score() <= self.state.score():
                # Doesn't improve the score
                continue
            graph[w] = GraphNode(new_game_state)
        print(self.state, len(graph), self.state.score())
        for w, g in graph.items():
            print(w)
            g.build_subgraph(w)



if __name__ == "__main__":

    graph = GraphNode(Game())
    graph.build_subgraph()
    print(graph)

    