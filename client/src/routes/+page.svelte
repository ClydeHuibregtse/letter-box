<script lang="ts">
	import BitBurndown from '../components/burndown.svelte';
	import { SolverClient } from '$lib/solutions';
	import Solution from '../components/solutions.svelte';
	import Input from '../components/input.svelte';
    import styles, { NORMALTEXT } from '../styles/constants.ts';
	
    let solverClient = new SolverClient();
    let inputLetters = '';

    let solnRes: any;
    let solnLetters: string;
    let binaryNumbers: string[];
    let isSolving = false;
    let errorMsg: string | null = null;

    function solnResToStates(solnRes: any) {
        return solnRes.solution.states.map((v: any) => v.id[1]);
    }

    async function getSolution(letters: string): Promise<any>{
        return await solverClient.solve(letters)
    }

    function handleClick() {
        isSolving = true;
        getSolution(inputLetters).then((res) => {
            solnRes = res;
            solnLetters = inputLetters;
            binaryNumbers = solnResToStates(solnRes);
            isSolving = false;
            errorMsg = null;
        }).catch((error) => {
            errorMsg = error;
            isSolving = false;
        });
    }

</script>

<div >

    <div class="{styles.TITLETEXT}">Letter Boxed Solver</div>

    <div class="centered w-full flex justify-center p-2">
        <Input bind:inputValue={inputLetters} handleSubmit={handleClick}/>
    </div>
    <div class="w-full h-full justify-center text-center">

        {#if isSolving}
            <div class="{styles.NORMALTEXT}">Solving...</div>
        {:else if errorMsg}
            <div class="text-3xl font-bold centered">
                <p>Error: {errorMsg}</p>
            </div>
        {:else if solnRes}
            <div class="grid grid-cols-2 gap-4">
                <div class="{styles.PANEL}">   
                    <div>
                        <p class="text-3xl font-bold underline centered">Bit Burndown Chart</p>
                        <BitBurndown binaryNumbers={binaryNumbers} letters={solnLetters} width={1000} height={1000}/>
                    </div>
                </div>
                <div class="border border-sky-500">
                    <Solution solution={solnRes}/>
                </div>
            </div>
        {:else}
            <div class="{styles.NORMALTEXT}">Enter some letters and click submit</div>
        {/if}
    </div>
    
</div>


<style lang="postcss">
    .grid-item {
        overflow: scroll;
        border: 1px solid black;
        padding: 10px;
    }
</style>
	