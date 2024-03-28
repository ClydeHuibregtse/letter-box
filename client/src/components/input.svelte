<script lang="ts">
    import styles, { BUTTON } from '../styles/constants.ts';
    export let inputValue = '';
    export let handleSubmit: () => void;
</script>


<div class="grid grid-rows-2 gap-2">
    <div class="flex justify-center">
        <input class="{styles.INPUT}" type="text" bind:value={inputValue} placeholder="Enter text" />
    </div>
    <div class="flex justify-center"> 
        <button class="{styles.BUTTON}" on:click={handleSubmit}>Submit</button>
    </div>
</div>