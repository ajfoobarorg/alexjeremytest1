<script>
  import { onMount } from 'svelte';
  import { navigate } from './router.js';
  import { isAuthenticated, myPlayerData } from './stores.js';
  import { calculateWinRate } from './utils.js';
  import SampleBoard from './SampleBoard.svelte';
  import MatchmakingModal from './MatchmakingModal.svelte';
  import { API_BASE_URL } from './config.js';

  // Game stats
  let gamesCount = 0;
  let playersOnline = 0;
  let showMatchmaking = false;

  async function fetchGameStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (response.ok) {
        const data = await response.json();
        gamesCount = data.games_today;
        playersOnline = data.players_online;
      }
    } catch (error) {
      console.error('Error fetching game stats:', error);
    }
  }

  onMount(async () => {
    await fetchGameStats();
    // Refresh stats every minute
    setInterval(fetchGameStats, 60000);
  });
</script>

<div class="home-container">
  {#if $isAuthenticated}
    <!-- Logged in view -->
    {#if $myPlayerData}
      <div class="user-stats">
        <div class="stat-item">
          <span class="stat-label">Rating</span>
          <span class="stat-value">{$myPlayerData.stats.elo}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Win Rate</span>
          <span class="stat-value">{calculateWinRate($myPlayerData.stats)}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Record</span>
          <span class="stat-value">{$myPlayerData.stats.wins}W-{$myPlayerData.stats.losses}L-{$myPlayerData.stats.draws}D</span>
        </div>
      </div>
    {/if}

    <div class="play-buttons">
      <button class="play-online-btn" on:click={() => showMatchmaking = true}>
        Play Online
      </button>
      <button class="play-bot-btn" disabled>
        Play Bots <span class="coming-soon">(Coming Soon)</span>
      </button>
    </div>
  {:else}
    <!-- Logged out view -->
    <div class="hero-section">
      <div class="sample-board-container">
        <SampleBoard />
      </div>
      
      <div class="hero-content">
        <h1>The World's Home for Ultimate Tic Tac Toe</h1>
        
        <div class="stats-row">
          <div class="stat">
            <span class="stat-number">{gamesCount.toLocaleString()}</span>
            <span class="stat-label">Games Today</span>
          </div>
          <div class="stat">
            <span class="stat-number">{playersOnline.toLocaleString()}</span>
            <span class="stat-label">Playing Now</span>
          </div>
        </div>

        <div class="play-buttons">
          <button class="play-online-btn" on:click={() => navigate('/signup')}>
            Play Online
          </button>
          <button class="play-bot-btn" disabled>
            Play Bots <span class="coming-soon">(Coming Soon)</span>
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

{#if showMatchmaking}
  <MatchmakingModal 
    playerId={$myPlayerData.id}
    onClose={() => showMatchmaking = false}
  />
{/if}

<style>
  .home-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  .hero-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
  }

  @media (max-width: 768px) {
    .hero-section {
      grid-template-columns: 1fr;
      gap: 2rem;
    }

    .sample-board-container {
      max-width: 400px;
      margin: 0 auto;
    }
  }

  .hero-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  h1 {
    font-size: clamp(2rem, 4vw, 3rem);
    color: #333;
    margin: 0;
    line-height: 1.2;
  }

  .stats-row {
    display: flex;
    gap: 2rem;
  }

  .stat {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-number {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
  }

  .stat-label {
    color: #666;
  }

  .user-stats {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .stat-item .stat-label {
    font-size: 0.9rem;
    color: #666;
  }

  .stat-item .stat-value {
    font-size: 1.1rem;
    font-weight: bold;
    color: #333;
  }

  .play-buttons {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 300px;
  }

  .play-online-btn {
    background: #2e7d32;
    color: white;
    border: none;
    padding: 1rem;
    border-radius: 4px;
    font-size: 1.1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .play-online-btn:hover {
    background: #1b5e20;
  }

  .play-bot-btn {
    background: #1976d2;
    color: white;
    border: none;
    padding: 1rem;
    border-radius: 4px;
    font-size: 1.1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .play-bot-btn:hover:not(:disabled) {
    background: #1565c0;
  }

  .play-bot-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .coming-soon {
    font-size: 0.9rem;
    font-weight: normal;
    opacity: 0.8;
  }
</style> 