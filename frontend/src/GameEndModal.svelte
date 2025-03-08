# This is a new file
<script>
  import { onMount } from 'svelte';
  import { playerStats } from './stores.js';
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  export let isWinner;
  export let isDraw;
  export let playerName;
  export let stats;
  
  let confetti;
  
  onMount(async () => {
    if (isWinner) {
      // Dynamically import confetti only when needed
      const module = await import('canvas-confetti');
      confetti = module.default;
      
      // Fire confetti
      const count = 200;
      const defaults = {
        origin: { y: 0.7 },
        zIndex: 1500
      };

      function fire(particleRatio, opts) {
        confetti({
          ...defaults,
          ...opts,
          particleCount: Math.floor(count * particleRatio),
        });
      }

      fire(0.25, {
        spread: 26,
        startVelocity: 55,
      });

      fire(0.2, {
        spread: 60,
      });

      fire(0.35, {
        spread: 100,
        decay: 0.91,
        scalar: 0.8
      });

      fire(0.1, {
        spread: 120,
        startVelocity: 25,
        decay: 0.92,
        scalar: 1.2
      });

      fire(0.1, {
        spread: 120,
        startVelocity: 45,
      });
    }
  });
</script>

<div class="modal-backdrop">
  <div class="modal">
    {#if isWinner}
      <h2>🎉 Congratulations, {playerName}! 🎉</h2>
      <p class="message">You've won the game!</p>
    {:else if isDraw}
      <h2>Game Over - It's a Draw!</h2>
      <p class="message">Well played by both players!</p>
    {:else}
      <h2>Good Game, {playerName}!</h2>
      <p class="message">You played well!</p>
    {/if}

    <div class="stats">
      <h3>Your Statistics</h3>
      <div class="stat-grid">
        <div class="stat">
          <span class="label">Wins</span>
          <span class="value">{stats.wins}</span>
        </div>
        <div class="stat">
          <span class="label">Losses</span>
          <span class="value">{stats.losses}</span>
        </div>
        <div class="stat">
          <span class="label">Draws</span>
          <span class="value">{stats.draws}</span>
        </div>
        <div class="stat">
          <span class="label">Win Rate</span>
          <span class="value">{((stats.wins / stats.totalGames) * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>

    <button class="dismiss-button" on:click={() => dispatch('close')}>
      Close
    </button>
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
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    max-width: 500px;
    width: 90%;
    text-align: center;
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from {
      transform: translateY(-20px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  h2 {
    color: #2e7d32;
    margin: 0 0 1rem 0;
  }

  .message {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    color: #424242;
  }

  .stats {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 8px;
  }

  h3 {
    color: #424242;
    margin: 0 0 1rem 0;
  }

  .stat-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .stat {
    background: white;
    padding: 1rem;
    border-radius: 6px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .label {
    display: block;
    color: #757575;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .value {
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
    color: #2e7d32;
  }

  .dismiss-button {
    margin-top: 1.5rem;
    padding: 0.8rem 2rem;
    background-color: #757575;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .dismiss-button:hover {
    background-color: #616161;
  }
</style> 