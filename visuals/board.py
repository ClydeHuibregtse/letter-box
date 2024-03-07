
from typing import List
from manimlib import (
    Scene,
    Circle,
    Square,
    ShowCreation,
    Write,
    ReplacementTransform,
    Transform,
    VGroup,
    DEGREES,
    Rotate,
    RIGHT,
    LEFT,
    UP,
    Write,
    Text,
    Line,
    always,
    BLUE,
    BLUE_E,
    ORANGE,
    GREEN
)



from letter_box.solve import build_letters, Oracle, solve

NODE_RADIUS = 0.3


def make_game_board(letters: List[str]):
    """Emit a Scene object with letters displayed"""
    S = len(letters) // 4

    d_node = NODE_RADIUS * 2 + 0.5 * NODE_RADIUS
    # Grid of size (S + 2) x (S + 2)
    max_y = max_x = (S + 1) / 2.0

    circles = []
    labels = []

    for i, letter in enumerate(letters):

        # Determine where on the board the letter lies
        side = i // S
        side_i = i - side * S

        if side == 0:
            # Top
            pos = (-max_x + (side_i + 1), max_y)

        elif side == 1:
            # Right
            pos = (max_x, max_y - (side_i + 1))

        elif side == 2:
            # Bottom
            pos = (max_x - (side_i + 1), -max_y)

        else:
            # Left
            pos = (-max_x, -(max_y - (side_i + 1)))

        circle = Circle(radius=NODE_RADIUS, stroke_color=BLUE_E)
        x, y = pos
        circle.move_to([x * d_node, y * d_node, 0])
        label = Text(letter)
        label.move_to(circle)

        circles.append(circle)
        labels.append(label)

    return circles, labels


class GameBoard(Scene):

    def initialize(self):
        """Set up board, and stash some references to certain mobjects"""

        global LETTERS
        global t
        LETTERS, t = solve()
        self.circles, self.labels = make_game_board(LETTERS)
        self.log = []
        g = VGroup(*(self.circles + self.labels))
        self.play(Write(g))
        self.wait(0.2)

    def write_path(self, path: List[int]):
        """Draw the lines for the path, highlight the letters,
        and move the word to the log"""
        word = ""
        text = Text(word)
        self.play(Write(text))
        for i, p in enumerate(path):
            word += LETTERS[p]
            new_text = Text(word)
            self.play(ReplacementTransform(text, new_text), run_time=0.05)
            text = new_text

            if i == len(path) - 1:
                continue

            c1, c2 = self.circles[p], self.circles[path[i + 1]]
            self.play(ShowCreation(Line(c1.get_center(), c2.get_center()), run_time=0.1))
            self.play(c1.animate.set_color(ORANGE), run_time=0.1)
            self.play(c2.animate.set_color(GREEN), run_time=0.1)

        # Update all logged words
        for past_word in self.log:
            self.play(past_word.animate.shift(1 * UP), run_time=0.1)
        self.log.append(text)
        self.play(text.animate.shift(5 * LEFT), run_time=0.1)

        self.wait(0.5)

    def construct(self):

        self.initialize()
        for p in t.paths:
            self.write_path(p)
