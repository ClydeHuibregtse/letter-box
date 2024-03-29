<script lang='ts'>
	import type { RunTime } from '$lib/solutions';
    import { onMount } from 'svelte';

    export let solution: any;

    function formatTime(runtime: RunTime) {
        return `${runtime.secs}.${runtime.nanos}s`;
    }

    function formatWords(words: string[]) {
        return words.join(', ');
    }

</script>

{#if solution === undefined}
    <p>No solution found</p>
{:else}
    <div class="grid">

        <div class="grid-item">Runtime:</div>
        <div class="grid-item">{formatTime(solution.meta.runtime)}</div>
        <div class="grid-item">Number of Words:</div>
        <div class="grid-item">{solution.solution.words.length}</div>
        <div class="grid-item">Words:</div>
        <div class="grid-item"> {formatWords(solution.solution.words)}</div>
        <div class="grid-item">States:</div>
        <div class="scrollable grid-item">
            {#each solution.solution.states as state}
                <p>{state.id[1]}</p>
            {/each}
        </div>
    </div>
{/if}

<style>
    .grid {
        display: grid;
        grid-template-columns: 1fr 2fr;
        grid-template-rows: 1fr 1fr 1fr 1fr 1fr;
        gap: 10px;
        padding: 5px;
    }
    .grid-item {
        height: 15vh;
    }
    .scrollable {
        width: 100%;
        overflow: scroll;
        border: 1px solid black;
    }
</style>
