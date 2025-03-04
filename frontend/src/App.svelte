<script>
  import { currentPath } from './router.js';
  import Home from './Home.svelte';
  import Game from './Game.svelte';

  $: path = $currentPath;
  $: gameId = path.startsWith('/game/') ? path.split('/game/')[1] : null;
</script>

<main>
  {#if path === '/'}
    <Home />
  {:else if gameId}
    <Game {gameId} />
  {:else}
    <p>Page not found</p>
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: Arial, sans-serif;
    background-color: #f9f9f9;
  }
</style> 