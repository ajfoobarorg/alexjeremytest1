# This is a new file
<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  export let playerXName;
  export let playerOName;
  export let playerXStats;
  export let playerOStats;
  
  let countdown = 3;
  let countdownInterval;
  
  onMount(() => {
    countdownInterval = setInterval(() => {
      countdown--;
      if (countdown <= 0) {
        clearInterval(countdownInterval);
        setTimeout(() => dispatch('start'), 500); // Small delay after countdown
      }
    }, 1000);
    
    return () => {
      if (countdownInterval) clearInterval(countdownInterval);
    };
  });
</script>

<div class="modal-backdrop">
  <div class="modal">
    <h2 class="match-title">Match Starting</h2>
    
    <div class="players">
      <div class="player x">
        <div class="player-name">{playerXName}</div>
        <div class="elo-rating">
          <span class="elo-value">{playerXStats?.elo || 800}</span>
          <span class="elo-label">ELO</span>
        </div>
      </div>
      
      <div class="vs">VS</div>
      
      <div class="player o">
        <div class="player-name">{playerOName}</div>
        <div class="elo-rating">
          <span class="elo-value">{playerOStats?.elo || 800}</span>
          <span class="elo-label">ELO</span>
        </div>
      </div>
    </div>
    
    <div class="countdown">
      Game starting in {countdown}...
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
    max-width: 600px;
    width: 90%;
    text-align: center;
    animation: slideIn 0.3s ease-out;
    box-sizing: border-box;
  }

  .match-title {
    margin: 0 0 1.5rem 0;
    color: #424242;
    font-size: 1.8rem;
  }

  .players {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
  }

  .player {
    flex: 1;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .player-name {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .player.x .player-name {
    color: #4CAF50;
  }

  .player.o .player-name {
    color: #2196F3;
  }

  .elo-rating {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #f5f5f5;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    min-width: 100px;
  }

  .player.x .elo-rating {
    border: 2px solid #4CAF50;
  }

  .player.o .elo-rating {
    border: 2px solid #2196F3;
  }

  .elo-value {
    font-size: 2rem;
    font-weight: bold;
    color: #424242;
  }

  .elo-label {
    font-size: 0.9rem;
    color: #757575;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .vs {
    font-size: 2rem;
    font-weight: bold;
    margin: 0 2rem;
    color: #424242;
  }

  .countdown {
    font-size: 1.5rem;
    font-weight: bold;
    color: #424242;
    margin-top: 2rem;
    animation: pulse 1s infinite;
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

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
  }

  /* Media queries for responsive design */
  @media (max-width: 600px) {
    .modal {
      padding: 1.5rem;
      width: 95%;
    }

    .match-title {
      font-size: 1.5rem;
      margin-bottom: 1rem;
    }

    .players {
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .player {
      width: 100%;
      padding: 0.5rem;
    }

    .player-name {
      font-size: 1.3rem;
    }

    .elo-value {
      font-size: 1.8rem;
    }

    .vs {
      margin: 0.5rem 0;
      font-size: 1.5rem;
    }

    .countdown {
      font-size: 1.3rem;
      margin-top: 1.5rem;
    }
  }

  @media (max-width: 400px) {
    .modal {
      padding: 1rem;
    }

    .player-name {
      font-size: 1.2rem;
    }

    .elo-value {
      font-size: 1.5rem;
    }

    .elo-label {
      font-size: 0.8rem;
    }
  }
</style> 