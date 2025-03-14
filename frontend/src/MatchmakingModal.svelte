<script>
  import { onMount, onDestroy } from 'svelte';
  import { navigate } from './router.js';
  import { API_BASE_URL } from './config.js';

  export let playerId;
  export let onClose;

  let status = 'Searching for opponent...';
  let error = null;
  let intervalId;
  let searchStartTime;
  let opponentName = null;
  let showCancelButton = true;
  const TIMEOUT_MS = 30000; // 30 seconds timeout

  async function startMatchmaking() {
    try {
      searchStartTime = Date.now();
      const response = await fetch(`${API_BASE_URL}/matchmaking/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: playerId
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        error = data.detail || 'Failed to start matchmaking';
        return;
      }

      // Start pinging for updates
      intervalId = setInterval(checkMatchStatus, 1000);
    } catch (err) {
      error = 'Failed to connect to matchmaking service';
      console.error('Matchmaking error:', err);
    }
  }

  async function checkMatchStatus() {
    try {
      // Check if we've exceeded the timeout
      if (Date.now() - searchStartTime >= TIMEOUT_MS) {
        error = 'No match found. Please try again.';
        await cancelMatchmaking();
        return;
      }

      const response = await fetch(`${API_BASE_URL}/matchmaking/ping`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: playerId
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        error = data.detail || 'Failed to check match status';
        return;
      }

      const data = await response.json();
      
      console.log('Matchmaking ping response:', data);  // Debug log
      
      if (data.status === 'matched') {
        // Game found and both players have accepted
        console.log('Match found, navigating to game:', data.game_id);
        
        // Clear interval and navigate
        clearInterval(intervalId);
        intervalId = null;
        navigate(`/game/${data.game_id}`);
      } else if (data.status === 'waiting_acceptance') {
        // Match found but waiting for both players to accept
        opponentName = data.opponent_name;
        showCancelButton = false;
        status = `Starting game with ${data.opponent_name}...`;
      } else if (data.status === 'waiting') {
        const timeElapsed = Math.floor((Date.now() - searchStartTime) / 1000);
        status = `Searching for opponent... (${30 - timeElapsed}s)`;
      }
    } catch (err) {
      error = 'Failed to check match status';
      console.error('Match status error:', err);
    }
  }

  async function cancelMatchmaking() {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }

    try {
      await fetch(`${API_BASE_URL}/matchmaking/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: playerId
        }),
      });
    } catch (err) {
      console.error('Error canceling matchmaking:', err);
    }
    
    onClose();
  }

  onMount(() => {
    startMatchmaking();
  });

  onDestroy(() => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
      cancelMatchmaking();
    }
  });
</script>

<div class="modal-backdrop">
  <div class="modal">
    <h2>Finding Match</h2>
    
    {#if error}
      <p class="error">{error}</p>
      <button on:click={onClose}>Close</button>
    {:else}
      <div class="loading-spinner"></div>
      <p class="status">{status}</p>
      {#if showCancelButton}
        <button class="cancel-button" on:click={cancelMatchmaking}>Cancel</button>
      {/if}
    {/if}
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    max-width: 400px;
    width: 90%;
    margin: 0 1rem;
    box-sizing: border-box;
  }

  @media (max-width: 480px) {
    .modal {
      padding: 1.5rem;
      width: 95%;
      margin: 0 0.5rem;
    }

    h2 {
      font-size: 1.4rem;
      margin-bottom: 1rem;
    }

    .status {
      font-size: 1rem;
    }

    button {
      padding: 0.7rem 1.2rem;
      font-size: 0.95rem;
    }

    .loading-spinner {
      width: 32px;
      height: 32px;
      border-width: 3px;
    }
  }

  h2 {
    margin: 0 0 1.5rem 0;
    color: #2e7d32;
  }

  .status {
    margin: 1rem 0;
    font-size: 1.1rem;
    color: #666;
  }

  .error {
    color: #f44336;
    margin: 1rem 0;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    margin: 1rem auto;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #2e7d32;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  button {
    background: #2e7d32;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover {
    background: #1b5e20;
  }

  .cancel-button {
    background: #f44336;
  }

  .cancel-button:hover {
    background: #d32f2f;
  }
</style> 