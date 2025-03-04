<script>
  import { onMount } from 'svelte';
  import { navigate } from './router.js';
  import { playerId, playerName } from './stores.js';
  import PlayerNameModal from './PlayerNameModal.svelte';

  let publicGames = [];
  let stats = { total_games: 0, completed_games: 0, ongoing_games: 0, x_wins: 0, o_wins: 0 };
  let isPublic = true;
  let gameName = '';
  let error = '';

  async function fetchPublicGames() {
    try {
      const response = await fetch('http://localhost:8000/games/public');
      publicGames = await response.json();
    } catch (error) {
      console.error('Error fetching public games:', error);
    }
  }

  async function fetchStats() {
    try {
      const response = await fetch('http://localhost:8000/stats');
      stats = await response.json();
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }

  async function createNewGame() {
    if (!$playerName) return;
    if (!gameName.trim()) {
      error = 'Please enter a game name';
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/games/new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          is_public: isPublic,
          player_id: $playerId,
          player_name: $playerName,
          game_name: gameName.trim()
        }),
      });
      const game = await response.json();
      navigate(`/game/${game.id}`);
    } catch (error) {
      console.error('Error creating new game:', error);
    }
  }

  async function joinGame(gameId) {
    if (!$playerName) return;

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
      const game = await response.json();
      navigate(`/game/${game.id}`);
    } catch (error) {
      console.error('Error joining game:', error);
    }
  }

  // Poll for updates
  let interval;
  onMount(() => {
    fetchPublicGames();
    fetchStats();
    interval = setInterval(() => {
      fetchPublicGames();
      fetchStats();
    }, 5000);

    return () => {
      clearInterval(interval);
    };
  });
</script>

{#if !$playerName}
  <PlayerNameModal />
{:else}
<main>
  <h1>Tic Tac Toe Games</h1>

  <div class="welcome">
    <p>Welcome, {$playerName}!</p>
  </div>

  <div class="stats">
    <h2>Game Statistics</h2>
    <p>Total Games: {stats.total_games}</p>
    <p>Ongoing Games: {stats.ongoing_games}</p>
    <p>Completed Games: {stats.completed_games}</p>
    <p>X Wins: {stats.x_wins}</p>
    <p>O Wins: {stats.o_wins}</p>
    <p>Draws: {stats.draws}</p>
  </div>

  <div class="new-game">
    <h2>Create New Game</h2>
    {#if error}
      <p class="error">{error}</p>
    {/if}
    <div class="form-group">
      <label for="game-name">Game Name:</label>
      <input 
        id="game-name"
        type="text" 
        bind:value={gameName}
        placeholder="Enter a name for your game"
      />
    </div>
    <label class="checkbox-label">
      <input type="checkbox" bind:checked={isPublic}>
      Make game public
    </label>
    <button on:click={createNewGame}>Create New Game</button>
  </div>

  <div class="public-games">
    <h2>Available Public Games</h2>
    {#if publicGames.length === 0}
      <p>No public games available</p>
    {:else}
      <ul>
        {#each publicGames as game}
          <li>
            <div class="game-info">
              <span class="game-name">{game.name}</span>
              <span class="player-name">Created by: {game.player_x_name}</span>
            </div>
            <button on:click={() => joinGame(game.id)}>Join Game</button>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</main>
{/if}

<style>
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    font-family: Arial, sans-serif;
  }

  h1 {
    color: #333;
    text-align: center;
    margin-bottom: 2rem;
  }

  h2 {
    color: #444;
    margin-top: 2rem;
  }

  .welcome {
    text-align: center;
    font-size: 1.2rem;
    margin-bottom: 2rem;
  }

  .stats {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .stats p {
    margin: 0.5rem 0;
  }

  .new-game {
    background: #e8f5e9;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
  }

  .form-group input {
    width: 100%;
    padding: 0.8rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  .checkbox-label {
    display: block;
    margin: 1rem 0;
  }

  .error {
    color: #f44336;
    margin: 0.5rem 0;
  }

  .public-games {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
  }

  ul {
    list-style: none;
    padding: 0;
  }

  li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    margin: 0.5rem 0;
    background: white;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  .game-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .game-name {
    font-weight: bold;
    font-size: 1.1rem;
  }

  .player-name {
    color: #666;
    font-size: 0.9rem;
  }

  button {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover {
    background-color: #45a049;
  }
</style> 