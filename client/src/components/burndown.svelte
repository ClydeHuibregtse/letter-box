<script lang="ts">
	import { onMount } from 'svelte';
    // import { addZUI } from '$lib/two_controls';
	import Two from 'two.js';

	export let binaryNumbers: string[] = [];
    export let letters: string = "";

    export let width: number;
    export let height: number;

	// Compute the twoContainer dimensions as a result
	// of the binaryNumbers array
	let twoContainer: HTMLElement;
	const RECT_SPACING = 0;

	let numRows: number;
	let numCols: number;
	$: {
		if (binaryNumbers.length == 0) {
			numRows = 0;
			numCols = 0;
		} else { 
            numRows = binaryNumbers.length;
            if (letters.length !== binaryNumbers[binaryNumbers.length - 1].length) {
                throw new Error('Length of letters must match length of the solution bits');
            }
			numCols = letters.length;
		}
	}

    function isBitSet(binaryNumber: string, index: number, num_bits: number) {
        while (binaryNumber.length < num_bits) {
            binaryNumber = '0' + binaryNumber;
        }
        return binaryNumber[index] === '1';
    }

	onMount(() => {

        // Compute the dimensions of the rectangles
        const rectWidth = width / (numCols + 1);
        // const rectHeight = height / (numRows + 1);
        const rectHeight = rectWidth;
        let x = rectWidth / 2 + rectWidth;
        let y = rectHeight / 2 + rectHeight;

        // Build the two app

		const two = new Two({
			width: width,
			height: height,
			autostart: true
		}).appendTo(twoContainer);
        // addZUI(two, twoContainer);

        // Populate cells
        for (let j = 0; j < numCols; j++) {
            two.makeText(
                letters[j],
                x + j * (rectWidth + RECT_SPACING),
                rectHeight / 2,
                {
                    family: 'Arial',
                    size: rectHeight / 2,
                    fill: 'black'
                }
            );
    		for (let i = 0; i < numRows; i++) {
                // Select color based on bit-set
                const rectColor = isBitSet(binaryNumbers[i], j, numCols) ? 'blue' : 'lightblue';
				const rect = two.makeRectangle(
					x + j * (rectWidth + RECT_SPACING),
					y + i * (rectHeight + RECT_SPACING),
					rectWidth,
					rectHeight
				);
				rect.fill = rectColor;
                rect.stroke = "white";
			}
		}
	});
</script>

<div class="scrollable padded">

    <div class="w-full" bind:this={twoContainer}></div>
</div>

<style>
    .scrollable {
        overflow: scroll;
    }
    .padded {
        padding: 5px;
    }
</style>
