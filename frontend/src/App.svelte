<script>
  let board = Array(9).fill("");
  let currentPlayer = "X";
  let winner = null;
  let gameOver = false;

  async function fetchGameState() {
    const response = await fetch('http://localhost:8000/game');
    const data = await response.json();
    board = data.board;
    currentPlayer = data.current_player;
    winner = data.winner;
    gameOver = data.game_over;
  }

  async function makeMove(position) {
    if (board[position] || gameOver) return;

    try {
      const response = await fetch(`http://localhost:8000/move/${position}`, {
        method: 'POST'
      });
      const data = await response.json();
      board = data.board;
      currentPlayer = data.current_player;
      winner = data.winner;
      gameOver = data.game_over;
    } catch (error) {
      console.error('Error making move:', error);
    }
  }

  async function resetGame() {
    try {
      const response = await fetch('http://localhost:8000/reset', {
        method: 'POST'
      });
      const data = await response.json();
      board = data.board;
      currentPlayer = data.current_player;
      winner = null;
      gameOver = false;
    } catch (error) {
      console.error('Error resetting game:', error);
    }
  }

  // Initial game state
  fetchGameState();
</script>

<main>
  <h1>Tic Tac Toe</h1>
  
  <div class="status">
    {#if winner}
      Winner: {winner}
    {:else if gameOver}
      Game Over - Draw!
    {:else}
      Current player: {currentPlayer}
    {/if}
  </div>

  <div class="board">
    {#each board as cell, i}
      <button class="cell" on:click={() => makeMove(i)}>
        {cell}
      </button>
    {/each}
  </div>

  <button class="reset" on:click={resetGame}>Reset Game</button>
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    font-family: Arial, sans-serif;
  }

  h1 {
    color: #333;
    margin-bottom: 2rem;
  }

  .status {
    margin-bottom: 2rem;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 2rem;
  }

  .cell {
    width: 100px;
    height: 100px;
    font-size: 2rem;
    font-weight: bold;
    border: 2px solid #333;
    background: white;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .cell:hover {
    background-color: #f0f0f0;
  }

  .reset {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .reset:hover {
    background-color: #45a049;
  }
</style> 