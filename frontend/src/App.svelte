<script>
  import { currentPath } from './router.js';
  import Home from './Home.svelte';
  import Game from './Game.svelte';

  $: path = $currentPath;
  $: gameId = path.startsWith('/game/') ? path.split('/game/')[1] : null;

  let board = Array(9).fill("");
  let currentPlayer = "X";
  let winner = null;
  let gameOver = false;

  async function fetchGameState() {
    const response = await fetch('http://localhost:8000/game');
    const data = await response.json();
    board = data.board;
    currentPlayer = data.current_player;
    winner = data.winner;
    gameOver = data.game_over;
  }

  async function makeMove(position) {
    if (board[position] || gameOver) return;

    try {
      const response = await fetch(`http://localhost:8000/move/${position}`, {
        method: 'POST'
      });
      const data = await response.json();
      board = data.board;
      currentPlayer = data.current_player;
      winner = data.winner;
      gameOver = data.game_over;
    } catch (error) {
      console.error('Error making move:', error);
    }
  }

  async function resetGame() {
    try {
      const response = await fetch('http://localhost:8000/reset', {
        method: 'POST'
      });
      const data = await response.json();
      board = data.board;
      currentPlayer = data.current_player;
      winner = null;
      gameOver = false;
    } catch (error) {
      console.error('Error resetting game:', error);
    }
  }

  // Initial game state
  fetchGameState();
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