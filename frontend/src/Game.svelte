<script>
  import { onMount } from 'svelte';
  import { playerId, playerName } from './stores.js';
  import { navigate } from './router.js';

  export let gameId;

  let board = Array(9).fill("");
  let currentPlayer = "X";
  let winner = null;
  let gameOver = false;
  let gameUrl = window.location.href;
  let isPlayer = false;
  let playerSymbol = null;
  let showCopiedMessage = false;
  let hasTriedToJoin = false;
  let gameName = "";
  let playerXName = null;
  let playerOName = null;

  async function tryJoinGame() {
    if (!$playerName) return false;
    
    try {
      const response = await fetch(`http://localhost:8000/games/${gameId}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: $playerId,
          player_name: $playerName
        })
      });
      if (response.ok) {
        const data = await response.json();
        return true;
      }
    } catch (error) {
      console.error('Error joining game:', error);
    }
    return false;
  }

  async function fetchGameState() {
    try {
      const response = await fetch(`http://localhost:8000/games/${gameId}`);
      const data = await response.json();
      board = data.board;
      currentPlayer = data.current_player;
      winner = data.winner;
      gameOver = data.game_over;
      gameName = data.name;
      playerXName = data.player_x_name;
      playerOName = data.player_o_name;
      
      // Reset player state
      isPlayer = false;
      playerSymbol = null;

      // Determine if current user is a player and which symbol they are
      if (data.player_x === $playerId) {
        isPlayer = true;
        playerSymbol = "X";
      } else if (data.player_o === $playerId) {
        isPlayer = true;
        playerSymbol = "O";
      } else if (!hasTriedToJoin && !data.player_o && !gameOver) {
        hasTriedToJoin = true;
        const joined = await tryJoinGame();
        if (joined) {
          await fetchGameState();
          return;
        }
      }

      // Update game URL to include the actual game ID
      gameUrl = window.location.origin + `/game/${gameId}`;
    } catch (error) {
      console.error('Error fetching game state:', error);
    }
  }

  async function makeMove(position) {
    if (!isPlayer || currentPlayer !== playerSymbol) return;
    
    try {
      const response = await fetch(`http://localhost:8000/games/${gameId}/move/${position}?player_id=${$playerId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
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

  function copyGameUrl() {
    navigator.clipboard.writeText(gameUrl);
    showCopiedMessage = true;
    setTimeout(() => {
      showCopiedMessage = false;
    }, 2000);
  }

  // Poll for updates
  let interval;
  onMount(() => {
    fetchGameState();
    interval = setInterval(fetchGameState, 1000);

    return () => {
      clearInterval(interval);
    };
  });
</script>

<main>
  <h1>{gameName}</h1>
  
  <div class="game-info">
    <button class="share" on:click={copyGameUrl}>
      {showCopiedMessage ? 'URL Copied!' : 'Share Game URL'}
    </button>
    <button class="home" on:click={() => navigate('/')}>Back to Home</button>
  </div>

  <div class="players">
    <div class="player player-x">
      <strong>Player X:</strong> {playerXName || 'Waiting...'}
    </div>
    <div class="player player-o">
      <strong>Player O:</strong> {playerOName || 'Waiting...'}
    </div>
  </div>

  <div class="status">
    {#if winner}
      Winner: {winner === 'X' ? playerXName : playerOName}!
    {:else if gameOver}
      Game Over - Draw!
    {:else if !isPlayer}
      {#if currentPlayer === "X" && !playerOName}
        Waiting for player O to join...
      {:else}
        Spectating - {currentPlayer === 'X' ? playerXName : playerOName}'s turn
      {/if}
    {:else if currentPlayer === playerSymbol}
      Your turn ({playerSymbol})
    {:else}
      Waiting for {currentPlayer === 'X' ? playerXName : playerOName} to move...
    {/if}
  </div>

  <div class="board">
    {#each board as cell, i}
      <button 
        class="cell" 
        on:click={() => makeMove(i)}
        disabled={!isPlayer || currentPlayer !== playerSymbol || cell || gameOver}
      >
        {cell}
      </button>
    {/each}
  </div>
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    font-family: Arial, sans-serif;
  }

  h1 {
    color: #333;
    margin-bottom: 2rem;
  }

  .game-info {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .players {
    display: flex;
    justify-content: space-around;
    width: 100%;
    max-width: 400px;
    margin-bottom: 2rem;
  }

  .player {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    background: #f5f5f5;
  }

  .player-x {
    color: #2196F3;
  }

  .player-o {
    color: #f44336;
  }

  .status {
    margin-bottom: 2rem;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 2rem;
  }

  .cell {
    width: 100px;
    height: 100px;
    font-size: 2rem;
    font-weight: bold;
    border: 2px solid #333;
    background: white;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .cell:not(:disabled):hover {
    background-color: #f0f0f0;
  }

  .cell:disabled {
    cursor: not-allowed;
    opacity: 0.8;
  }

  button {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .share {
    background-color: #2196F3;
    color: white;
  }

  .share:hover {
    background-color: #1976D2;
  }

  .home {
    background-color: #757575;
    color: white;
  }

  .home:hover {
    background-color: #616161;
  }
</style> 