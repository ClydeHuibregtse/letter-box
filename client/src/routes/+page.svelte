<script lang="ts">
	import { Board } from '$lib/gameboard.ts';
	import { onMount } from 'svelte';
	import Two from 'two.js';

	let letters: string = '01234567890123456789';
	let two: Two;
	let twoContainer: HTMLElement;

	function drawScene(two: Two, letters: string) {
		let board = new Board(letters);
		let letterGroups = board.drawBoard(two);
	}
	function setup(letters: string) {
		// Create a new instance of Two.js and attach it to the container
		if (twoContainer == undefined) {
			return;
		}
		two = new Two({
			width: twoContainer.offsetWidth,
			height: twoContainer.offsetHeight
		}).appendTo(twoContainer);

		// Draw your shapes here
		drawScene(two, letters);

		// Update the rendering
		two.update();

		// Cleanup on component unmount
		return () => {
			two.clear(); // Clear the canvas
			two.unbind('resize'); // Unbind any resize event listeners
		};
	}

	function refresh(letters: string) {
		if (two == null) {
			return;
		}
		two.clear();
		try {
			drawScene(two, letters);
		} catch {
			return;
		}
		two.update();
	}

	$: {
		refresh(letters);
	}

	onMount(() => {
		setup(letters);
	});
</script>

<svelte:window
	on:resize={(event) => {
		refresh(letters);
	}}
/>

<div class="grid-container">
	<div class="grid-item"></div>
	<div class="grid-item"></div>
	<div class="grid-item"></div>

	<div class="grid-item"></div>
	<div class="grid-item">
		<div bind:this={twoContainer} id="two-container"></div>
	</div>

	<div class="grid-item">
		<input type="text" id="letters" bind:value={letters} placeholder="Enter some letters" />
	</div>

	<div class="grid-item"></div>
	<div class="grid-item"></div>
	<div class="grid-item"></div>
</div>

<style>
	#two-container {
		background-color: antiquewhite;
		width: 100%;
		height: 100%;
	}

	.grid-container {
		height: 100vh;
		display: grid;
		grid-template-columns: 1fr 3fr 3fr; /* Three columns of equal width */
		grid-template-rows: 1fr 3fr 1fr; /* Three columns of equal width */
		grid-gap: 10px; /* Gap between grid items */
		background-color: antiquewhite;
	}

	.grid-item {
		background-color: antiquewhite;
		padding: 20px;
		text-align: center;
		/* background-color: black; */
	}
</style>
