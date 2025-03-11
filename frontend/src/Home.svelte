<script>
  import { onMount } from 'svelte';
  import { navigate } from './router.js';
  import { playerId } from './stores.js';
  import PlayerNameModal from './PlayerNameModal.svelte';
  import MatchmakingModal from './MatchmakingModal.svelte';
  import { API_BASE_URL } from './config.js';

  // Player data
  let player = null;
  
  // UI state
  let isLoading = true;
  let showMatchmaking = false;

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

  onMount(async () => {
    await fetchPlayerData();
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

  <div class="find-match">
    <h2>Play Online</h2>
    <button class="find-match-button" on:click={() => showMatchmaking = true}>
      Let's play!
    </button>
  </div>

  {#if showMatchmaking}
    <MatchmakingModal 
      playerId={$playerId}
      onClose={() => showMatchmaking = false}
    />
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

  .find-match {
    background: #e8f5e9;
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    text-align: center;
  }

  .find-match h2 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #2e7d32;
  }

  .find-match-button {
    background: #2e7d32;
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 4px;
    font-size: 1.2rem;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .find-match-button:hover {
    background: #1b5e20;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }

  .find-match-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .loading {
    text-align: center;
    padding: 2rem;
    font-size: 1.2rem;
    color: #666;
  }
</style> 