<script>
  import { onMount } from 'svelte';
  import { navigate } from './router.js';
  import { playerId } from './stores.js';
  import PlayerNameModal from './PlayerNameModal.svelte';
  import { API_BASE_URL } from './config.js';
  import { calculateTotalGames, calculateWinRate } from './utils.js';

  // Game data
  let publicGames = [];
  let isPublic = true;
  let gameName = '';
  
  // Player data
  let player = null;
  
  // UI state
  let error = '';
  let isLoading = true;

  async function fetchPublicGames() {
    try {
      const response = await fetch(`${API_BASE_URL}/games/public`);
      publicGames = await response.json();
    } catch (error) {
      console.error('Error fetching public games:', error);
    }
  }

  async function fetchPlayerData() {
    try {
      const response = await fetch(`${API_BASE_URL}/players/${$playerId}`);
      if (response.ok) {
        player = await response.json();
      }
    } catch (error) {
      console.error('Error fetching player data:', error);
    } finally {
      isLoading = false;
    }
  }

  async function createNewGame() {
    if (!player?.name) return;
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
          game_name: gameName.trim()
        }),
      });
      const game = await response.json();
      navigate(`/game/${game.id}`);
    } catch (error) {
      console.error('Error creating new game:', error);
    }
  }

  onMount(async () => {
    await fetchPlayerData();
    await fetchPublicGames();
    
    // Refresh public games list periodically
    const interval = setInterval(fetchPublicGames, 5000);
    return () => clearInterval(interval);
  });
</script>

{#if isLoading}
  <div class="loading">Loading...</div>
{:else if !player?.name}
  <PlayerNameModal />
{:else}
<main>
  <h1>Ultimate Tic-Tac-Toe</h1>
  
  <div class="player-info">
    <h2 class="player-name">{player.name} <span class="elo">({player.elo})</span></h2>
    <p class="player-stats">{player.wins} wins / {player.draws} draws / {player.losses} losses</p>
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

  {#if publicGames.length > 0}
    <div class="public-games">
      <h2>Join a Public Game</h2>
      <div class="games-list">
        {#each publicGames as game}
          <div class="game-item">
            <span class="game-name">{game.name}</span>
            <span class="creator-name">Created by: {game.player_x.name}</span>
            <button on:click={() => navigate(`/game/${game.id}`)}>
              Join Game
            </button>
          </div>
        {/each}
      </div>
    </div>
  {/if}
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

  .player-info {
    background: #e8f5e9;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 600px;
    margin: 0 auto 2rem auto;
    text-align: center;
    border: 2px solid #2e7d32;
    transition: transform 0.2s;
  }

  .player-info:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .player-name {
    margin: 0 0 0.5rem 0;
    color: #2e7d32;
    font-size: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .elo {
    font-weight: bold;
    color: #2e7d32;
    white-space: nowrap;
  }

  .player-stats {
    margin: 0;
    font-size: 1.1rem;
    color: #424242;
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

  .games-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .game-item {
    background: white;
    padding: 1rem;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .game-name {
    font-weight: bold;
    font-size: 1.1rem;
  }

  .creator-name {
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

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-size: 1.2rem;
    color: #666;
  }

  /* Media queries for responsive design */
  @media (max-width: 600px) {
    main {
      padding: 1rem;
    }

    .player-info {
      padding: 1rem;
    }

    .player-name {
      font-size: 1.5rem;
    }

    .player-stats {
      font-size: 1rem;
    }
  }

  @media (max-width: 400px) {
    .player-name {
      font-size: 1.3rem;
    }

    .player-stats {
      font-size: 0.9rem;
    }
  }
</style> 