from typing import Tuple, Iterator, List

from manim import *
from manim.typing import Vector3


SceneCoord = Tuple[Vector3, Vector3]
"""Type alias for a position on the scene frame"""

LetterNode = VGroup
"""Type alias for a node on the board"""


class Board:
    """Methods for creating visuals with Letter Boxed geometries"""

    @staticmethod
    def coord_at_index(i: int, S: int) -> SceneCoord:
        """Get the coordinate for a letter's position on the board"""

        # Grid of size (S + 2) x (S + 2)
        # Determine where on the board the letter lies
        side = i // S
        side_i = i - side * S

        side_scale = (S / 2.0 - 0.5) + 1
        max_left = LEFT * side_scale
        max_right = RIGHT * side_scale
        max_up = UP * side_scale
        max_down = DOWN * side_scale

        if side == 0:
            # Top
            return (
                (max_left + (side_i + 1) * RIGHT)
                + max_up
            )

        elif side == 1:
            # Right
            return (
                max_right
                + max_up + (side_i + 1) * DOWN
            )

        elif side == 2:
            # Bottom
            return (
                (max_right + (side_i + 1) * LEFT)
                + max_down
            )

        else:
            # Left
            return (
                max_left
                - (max_up + (side_i + 1) * DOWN)
            )

    @staticmethod
    def all_coords(S: int) -> Iterator[SceneCoord]:
        """Yield all coords"""
        for i in range(S * 4):
            yield Board.coord_at_index(i, S)

    @staticmethod
    def make_letter_node_mobject(letter: str, radius: float = 1.0) -> LetterNode:
        """Create mobject for a letter node"""
        circle = Circle(radius=radius)
        text = Text(letter)
        return LetterNode(circle, text)

    @staticmethod
    def make_word_arrows(word: str, nodes: List[LetterNode], letters: str) -> List[Arrow]:
        """Create a collection of arrows connecting letters in a word"""
        arrows = list()
        for i, letter in enumerate(word[:-1]):
            # Get current node and next node
            tail = nodes[letters.index(letter)]
            head = nodes[letters.index(word[i + 1])]
            arrow = Arrow(tail.get_center(), head.get_center())
            arrows.append(arrow)
        return arrows


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    coords = np.array([c for c in Board.all_coords(4)])
    print(coords)
    plt.scatter(coords[:, 0], coords[:, 1])
    plt.show()
