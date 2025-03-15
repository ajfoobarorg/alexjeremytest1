<script>
  // Sample game state with some moves already made
  const sampleBoard = [
    // Top row of big squares
    [
      ['X', 'O', 'X', 'O', '', '', '', 'X', 'O'],  // Top left
      ['X', 'O', 'X', 'O', 'X', 'O', '', '', ''],  // Top middle (X won)
      ['O', '', '', 'X', 'O', '', '', '', 'X']     // Top right
    ],
    // Middle row of big squares
    [
      ['', '', '', 'O', 'X', '', '', '', ''],      // Middle left
      ['O', 'X', '', '', 'O', 'X', '', '', ''],    // Center
      ['X', '', '', '', 'O', '', '', '', '']       // Middle right
    ],
    // Bottom row of big squares
    [
      ['O', 'X', 'O', 'X', 'O', 'X', 'O', 'X', 'O'], // Bottom left (O won)
      ['', '', '', '', '', '', '', '', ''],         // Bottom middle
      ['X', '', '', '', 'O', '', '', '', '']       // Bottom right
    ]
  ];

  // Function to check if a small board is won
  function isSmallBoardWon(board) {
    // Winning combinations
    const lines = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
      [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
      [0, 4, 8], [2, 4, 6]             // Diagonals
    ];

    for (let line of lines) {
      const [a, b, c] = line;
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return board[a];
      }
    }
    return null;
  }
</script>

<div class="board-container">
  <div class="big-board">
    {#each sampleBoard as row, i}
      <div class="big-row">
        {#each row as smallBoard, j}
          <div class="big-square">
            {#if isSmallBoardWon(smallBoard)}
              <div class="winner-overlay">
                {isSmallBoardWon(smallBoard)}
              </div>
            {/if}
            <div class="small-board">
              {#each smallBoard as cell, k}
                <div class="cell">
                  {#if cell}
                    <span class={cell}>{cell}</span>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {/each}
  </div>
</div>

<style>
  .board-container {
    width: 100%;
    max-width: 500px;
    aspect-ratio: 1;
    margin: 0 auto;
  }

  .big-board {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    height: 100%;
    background: #f5f5f5;
    padding: 8px;
    border-radius: 8px;
  }

  .big-row {
    display: flex;
    gap: 8px;
    flex: 1;
  }

  .big-square {
    flex: 1;
    background: white;
    border-radius: 4px;
    padding: 4px;
    position: relative;
  }

  .small-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 2px;
    width: 100%;
    height: 100%;
  }

  .cell {
    background: #f8f8f8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(0.8rem, 2vw, 1.2rem);
    font-weight: bold;
    aspect-ratio: 1;
  }

  .X {
    color: #f44336;
  }

  .O {
    color: #2196f3;
  }

  .winner-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: bold;
    border-radius: 4px;
  }

  .winner-overlay:global(.X) {
    color: #f44336;
  }

  .winner-overlay:global(.O) {
    color: #2196f3;
  }
</style> 