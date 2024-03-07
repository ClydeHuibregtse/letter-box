from manim import *
from boards import Board

NODE_CREATE_TIME = 0.1
ARROW_CREATE_TIME = 0.2
TEXT_CREATE_TIME = 0.2
WAIT_TIME = 1.0

class IntroBoard(Scene):
    def construct(self):

        # From 11/26/2023!
        letters = "eicaoxtufrvg"

        # Build board
        nodes = []
        S = len(letters) // 4
        for i, letter in enumerate(letters):

            coord = Board.coord_at_index(i, S) * 1.5
            node = Board.make_letter_node_mobject(letter, 1.0 / S)
            self.play(Create(node), run_time=NODE_CREATE_TIME)
            self.play(ApplyMethod(node.shift, coord), run_time=NODE_CREATE_TIME)
            nodes.append(node)

        self.play(Wait(run_time=0.5))

        # Rule 1
        # A good example: cat -> toe
        cat_arrows = Board.make_word_arrows("cat", nodes, letters)
        toe_arrows = Board.make_word_arrows("toe", nodes, letters)

        for arrow in cat_arrows:
            self.play(Create(arrow), run_time=ARROW_CREATE_TIME)
        self.play(Wait(run_time=WAIT_TIME / 2.0))

        for arrow in toe_arrows:
            self.play(Create(arrow), run_time=ARROW_CREATE_TIME)

        status = Text("Valid!")
        self.play(Create(status), run_time=TEXT_CREATE_TIME)

        self.play(Wait(run_time=WAIT_TIME))
        self.play(FadeOut(*(cat_arrows + toe_arrows + [status])))

        # A bad example: cat -> rug
        cat_arrows = Board.make_word_arrows("cat", nodes, letters)
        rug_arrows = Board.make_word_arrows("rug", nodes, letters)

        for arrow in cat_arrows:
            self.play(Create(arrow), run_time=ARROW_CREATE_TIME)
        self.play(Wait(run_time=WAIT_TIME / 2.0))

        for arrow in rug_arrows:
            self.play(Create(arrow), run_time=ARROW_CREATE_TIME)

        status = Text("Invalid!")
        self.play(Create(status), run_time=TEXT_CREATE_TIME)

        self.play(Wait(run_time=WAIT_TIME))
        self.play(FadeOut(*(cat_arrows + rug_arrows + [status])))

        self.play(Wait(run_time=WAIT_TIME))

        # Rule 2
        # A bad example
        coax_arrows = Board.make_word_arrows("coax", nodes, letters)
        for arrow in coax_arrows:
            self.play(Create(arrow), run_time=ARROW_CREATE_TIME)
        self.play(Wait(run_time=WAIT_TIME))
        status = Text("Invalid!")
        self.play(Create(status), run_time=TEXT_CREATE_TIME)