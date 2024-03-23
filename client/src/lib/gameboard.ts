import type Two from 'two.js';
import type { Group } from 'two.js/src/group';

interface LetterCell {
	x: number;
	y: number;
	letter: string;
}

export class Board {
	static paddingFactor: number = 0.08;

	letters: string;

	constructor(letters: string) {
		if (letters.length % 4 != 0) {
			throw new Error();
		}
		this.letters = letters;
	}

	/**
	 * Calculate positions for each letter on the board.
	 * @returns An array of `LetterCell` objects representing the positions and letters on the board.
	 */
	letterPositions(): LetterCell[] {
		let numPerSide = this.letters.length / 4;
		let cells: LetterCell[] = [];
		let numCells = 0;

		let right = numPerSide + 1;
		let bottom = numPerSide + 1;
		let left = 0;
		let top = 0;

		for (let j = 0; j < numPerSide + 2; j++) {
			for (let i = 0; i < numPerSide + 2; i++) {
				// Top and Bottom
				if ((j == bottom || j == top) && i != left && i != right) {
					cells.push({
						x: i,
						y: j,
						letter: this.letters[numCells]
					});
					numCells += 1;
				}
				// Left and Right
				if ((i == left || i == right) && j != top && j != bottom) {
					cells.push({
						x: i,
						y: j,
						letter: this.letters[numCells]
					});
					numCells += 1;
				}
			}
		}
		return cells;
	}

	/**
	 * Draw the game board and return an array of letter container groups.
	 * @param two - The Two.js instance used for drawing.
	 * @returns An array of `Group` objects representing the letter container groups.
	 */
	drawBoard(two: Two): Group[] {
		// Draw the gameboard and return an array of letter
		// container groups1

		// slight padding off the edges
		let xPadding = Board.paddingFactor * two.width;
		let yPadding = Board.paddingFactor * two.height;

		let width = two.width - 2 * xPadding;
		let height = two.height - 2 * yPadding;

		// Spacing between adjacent lattice points in the grid
		let numPerSide = this.letters.length / 4.0 + 2;
		let xSpacing = width / (numPerSide - 1);
		let ySpacing = height / (numPerSide - 1);

		let center = [xPadding, yPadding];

		let letterCells = this.letterPositions();
		let letterGroup = two.makeGroup();
		let letterRenders: Group[] = [];
		letterCells.forEach((v, i, a) => {
			let x_trans = v.x * xSpacing;
			let y_trans = v.y * ySpacing;

			let letterRender = this.drawLetter(two, v.letter, x_trans, y_trans, xSpacing, ySpacing);
			letterGroup.add(letterRender);
			letterRenders.push(letterRender);
		});
		letterGroup.translation.set(center[0], center[1]);
		return letterRenders;
	}

	/**
	 * Draw a letter at a specified position on the board.
	 * @param two - The Two.js instance used for drawing.
	 * @param letter - The letter to be drawn.
	 * @param x - The x-coordinate of the letter's position.
	 * @param y - The y-coordinate of the letter's position.
	 * @param width - The width of the letter's bounding rectangle.
	 * @param height - The height of the letter's bounding rectangle.
	 * @returns A `Group` object representing the letter container group.
	 */
	drawLetter(two: Two, letter: string, x: number, y: number, width: number, height: number): Group {
		let group = two.makeGroup();

		// Bounding rectangle
		// let rect = two.makeRectangle(x, y, width, height);

		// rect.on("click", (event: any) => console.log(event));

		// Letter char
		let letterStyle = {
			size: 45,
			alignment: 'center' // Text alignment
		};
		let char = two.makeText(letter, x, y, letterStyle);

		// Add everything to the group and return
		// group.add(rect);
		group.add(char);
		return group;
	}
}
