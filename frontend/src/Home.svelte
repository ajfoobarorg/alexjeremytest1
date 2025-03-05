<script>
  import { onMount } from 'svelte';
  import { navigate } from './router.js';
  import { playerId, playerName, playerStats } from './stores.js';
  import PlayerNameModal from './PlayerNameModal.svelte';
  import { API_BASE_URL } from './config.js';

  let publicGames = [];
  let stats = { total_games: 0, completed_games: 0, ongoing_games: 0, x_wins: 0, o_wins: 0 };
  let isPublic = true;
  let gameName = '';
  let error = '';

  async function fetchPublicGames() {
    try {
      const response = await fetch(`${API_BASE_URL}/games/public`);
      publicGames = await response.json();
    } catch (error) {
      console.error('Error fetching public games:', error);
    }
  }

  async function fetchStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
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
      const response = await fetch(`${API_BASE_URL}/games/new`, {
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
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/join`, {
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

  <div class="stats-container">
    <div class="stats">
      <h2>Global Scores</h2>
      <div class="stat-grid">
        <div class="stat-item">
          <span class="label">Total Games</span>
          <span class="value">{stats.total_games}</span>
        </div>
        <div class="stat-item">
          <span class="label">Ongoing Games</span>
          <span class="value">{stats.ongoing_games}</span>
        </div>
        <div class="stat-item">
          <span class="label">X Wins</span>
          <span class="value">{stats.x_wins}</span>
        </div>
        <div class="stat-item">
          <span class="label">O Wins</span>
          <span class="value">{stats.o_wins}</span>
        </div>
        <div class="stat-item">
          <span class="label">Draws</span>
          <span class="value">{stats.draws}</span>
        </div>
        <div class="stat-item">
          <span class="label">Completed</span>
          <span class="value">{stats.completed_games}</span>
        </div>
      </div>
    </div>

    <div class="stats personal">
      <h2>Your Scores</h2>
      <div class="stat-grid">
        <div class="stat-item">
          <span class="label">Total Games</span>
          <span class="value">{$playerStats.totalGames}</span>
        </div>
        <div class="stat-item">
          <span class="label">Wins</span>
          <span class="value">{$playerStats.wins}</span>
        </div>
        <div class="stat-item">
          <span class="label">Losses</span>
          <span class="value">{$playerStats.losses}</span>
        </div>
        <div class="stat-item">
          <span class="label">Draws</span>
          <span class="value">{$playerStats.draws}</span>
        </div>
        <div class="stat-item">
          <span class="label">Win Rate</span>
          <span class="value">{(($playerStats.wins / ($playerStats.totalGames || 1)) * 100).toFixed(1)}%</span>
        </div>
        <div class="stat-item highlight">
          <span class="label">Best Streak</span>
          <span class="value">Coming soon!</span>
        </div>
      </div>
    </div>
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

  .stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    width: 100%;
    margin-bottom: 2rem;
  }

  .stats {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .stats.personal {
    background: #e8f5e9;  /* Light green background for personal stats */
  }

  .stat-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-top: 1rem;
  }

  .stat-item {
    background: white;
    padding: 1rem;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
  }

  .stat-item:hover {
    transform: translateY(-2px);
  }

  .stat-item.highlight {
    border: 2px solid #4CAF50;
  }

  .label {
    display: block;
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .value {
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
    color: #2e7d32;
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