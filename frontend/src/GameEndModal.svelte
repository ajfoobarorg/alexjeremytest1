# This is a new file
<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { navigate } from './router.js';
  
  const dispatch = createEventDispatcher();
  
  export let isWinner;
  export let isDraw;
  export let playerName;
  export let stats;
  export let eloChange;
  export let oldElo;
  
  let confetti;
  
  function handleClose() {
    dispatch('dismiss');
  }
  
  function goToHome() {
    navigate('/');
  }
  
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

<div class="modal-backdrop" on:click={handleClose}>
  <div class="modal" on:click|stopPropagation>
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

    <div class="elo-container">
      <div class="elo-change {eloChange > 0 ? 'positive' : eloChange < 0 ? 'negative' : 'neutral'}">
        <span class="elo-label">ELO Rating:</span>
        <span class="elo-value">
          {oldElo} → {stats.elo}
        </span>
      </div>
    </div>

    <div class="button-container">
      <button class="dismiss-button" on:click={handleClose}>
        Close
      </button>
      <button class="home-button" on:click={goToHome}>
        Back to Home
      </button>
    </div>
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
    box-sizing: border-box;
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
    margin-bottom: 1.5rem;
    color: #424242;
  }

  .elo-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .elo-change {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 8px;
    width: 100%;
    text-align: center;
    font-size: 1.2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .elo-change.positive {
    background: #e8f5e9;
    border: 2px solid #2e7d32;
  }

  .elo-change.negative {
    background: #ffebee;
    border: 2px solid #c62828;
  }

  .elo-change.neutral {
    background: #e3f2fd;
    border: 2px solid #1565c0;
  }

  .elo-label {
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #424242;
  }

  .elo-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .elo-value.positive {
    color: #2e7d32;
  }

  .elo-value.negative {
    color: #c62828;
  }

  .button-container {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
  }

  .dismiss-button, .home-button {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
    position: relative;
    z-index: 1010;
  }

  .dismiss-button {
    background-color: #757575;
    color: white;
  }

  .dismiss-button:hover {
    background-color: #616161;
  }

  .home-button {
    background-color: #4CAF50;
    color: white;
  }

  .home-button:hover {
    background-color: #45a049;
  }

  /* Media queries for responsive design */
  @media (max-width: 600px) {
    .modal {
      padding: 1.5rem;
      width: 95%;
    }

    h2 {
      font-size: 1.5rem;
    }

    .message {
      font-size: 1rem;
      margin-bottom: 1rem;
    }

    .elo-value {
      font-size: 2rem;
    }

    .button-container {
      gap: 0.5rem;
    }

    .dismiss-button, .home-button {
      padding: 0.6rem 1rem;
      font-size: 0.9rem;
    }
  }

  @media (max-width: 400px) {
    .modal {
      padding: 1rem;
    }

    h2 {
      font-size: 1.3rem;
    }

    .elo-value {
      font-size: 1.8rem;
    }
  }
</style> 