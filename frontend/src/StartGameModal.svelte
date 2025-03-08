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
    <div class="players">
      <div class="player x">
        <h2>{playerXName}</h2>
        <div class="stats">
          <div>Wins: {playerXStats?.wins || 0}</div>
          <div>Losses: {playerXStats?.losses || 0}</div>
          <div>Draws: {playerXStats?.draws || 0}</div>
        </div>
      </div>
      
      <div class="vs">VS</div>
      
      <div class="player o">
        <h2>{playerOName}</h2>
        <div class="stats">
          <div>Wins: {playerOStats?.wins || 0}</div>
          <div>Losses: {playerOStats?.losses || 0}</div>
          <div>Draws: {playerOStats?.draws || 0}</div>
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
  }

  .player.x h2 {
    color: #4CAF50;
  }

  .player.o h2 {
    color: #2196F3;
  }

  .vs {
    font-size: 2rem;
    font-weight: bold;
    margin: 0 2rem;
    color: #424242;
  }

  .stats {
    margin-top: 1rem;
    font-size: 1.1rem;
    color: #616161;
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

    .players {
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .player {
      width: 100%;
      padding: 0.5rem;
    }

    .vs {
      margin: 0.5rem 0;
      font-size: 1.5rem;
    }

    h2 {
      font-size: 1.3rem;
      margin: 0.5rem 0;
    }

    .stats {
      margin-top: 0.5rem;
      font-size: 1rem;
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

    .stats {
      font-size: 0.9rem;
    }
  }
</style> 