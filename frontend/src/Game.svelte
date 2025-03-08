<script>
  import { onMount, onDestroy } from 'svelte';
  import { playerId } from './stores.js';
  import { navigate } from './router.js';
  import PlayerNameModal from './PlayerNameModal.svelte';
  import GameEndModal from './GameEndModal.svelte';
  import { API_BASE_URL } from './config.js';
  import StartGameModal from './StartGameModal.svelte';
  import { calculateTotalGames, calculateWinRate } from './utils.js';

  export let gameId;

  // Game state
  let boards = Array(9).fill(null).map(() => Array(9).fill(""));
  let metaBoard = Array(9).fill("");
  let currentPlayer = "X";
  let winner = null;
  let gameOver = false;
  let nextBoard = null;
  let gameStarted = false;
  
  // Game metadata
  let gameName = "";
  let gameUrl = window.location.href;
  
  // Player information
  let player = null; // Current player data including name and stats
  let playerSymbol = null;
  let isPlayer = false;
  let opponent = null; // Opponent data including name and stats
  
  // Player references from game
  let playerX = null;
  let playerO = null;
  
  // UI state
  let showCopiedMessage = false;
  let hasTriedToJoin = false;
  let showGameEndModal = false;
  let gameEndModalDismissed = false;
  let showStartGameModal = false;
  let startGameModalShown = false; // Track if start game modal has been shown
  let isLoading = true;
  let showResignConfirm = false;

  // Timing variables
  let lastUpdateTime = null;
  let serverPlayerXTimeRemaining = null;
  let serverPlayerOTimeRemaining = null;
  let displayedXTimeRemaining = null;
  let displayedOTimeRemaining = null;
  let warningCountdown = null;
  let warningInterval;
  let pollInterval;
  let timeUpdateInterval;

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

  $: if ($playerId) {
    fetchPlayerData();
  }

  $: if (player?.name) {
    hasTriedToJoin = false;
  }

  $: if (gameOver && !showGameEndModal && !gameEndModalDismissed) {
    if (isPlayer) {
      showGameEndModal = true;
      // Refresh player data to show updated stats in modal
      fetchPlayerData();
    }
  }

  $: isMyTurn = currentPlayer === 'X' ? playerX === $playerId : playerO === $playerId;
  $: timeRemaining = currentPlayer === 'X' ? displayedXTimeRemaining : displayedOTimeRemaining;
  $: showWarning = isMyTurn && (warningCountdown !== null || (timeRemaining !== null && timeRemaining <= 25)) && !gameOver;

  function updateDisplayTimes() {
    if (gameOver || lastUpdateTime === null) return;
    
    const now = Date.now();
    const elapsed = Math.floor((now - lastUpdateTime) / 1000);
    
    // Only update if a full second has passed
    if (elapsed > 0) {
      // Only decrement time for the current player
      if (currentPlayer === 'X') {
        displayedXTimeRemaining = Math.max(0, serverPlayerXTimeRemaining - elapsed);
        displayedOTimeRemaining = serverPlayerOTimeRemaining;
      } else {
        displayedOTimeRemaining = Math.max(0, serverPlayerOTimeRemaining - elapsed);
        displayedXTimeRemaining = serverPlayerXTimeRemaining;
      }
      
      // Check for warning conditions based on inactivity
      if (isMyTurn && elapsed >= 15 && !warningInterval) {  // Show warning after 15 seconds of inactivity
        startWarningCountdown();
      }
    }
  }

  function updateTimesFromServer(xTime, oTime) {
    // Don't start timing until both players have joined and countdown is complete
    if (!gameStarted || !playerO) return;

    // Initialize the timer if this is the first update
    if (lastUpdateTime === null) {
      timeUpdateInterval = setInterval(updateDisplayTimes, 1000);  // Update every second instead of 100ms
    }
    
    // Only update the times if they've changed from the server
    if (xTime !== serverPlayerXTimeRemaining || oTime !== serverPlayerOTimeRemaining) {
      serverPlayerXTimeRemaining = xTime;
      serverPlayerOTimeRemaining = oTime;
      displayedXTimeRemaining = xTime;
      displayedOTimeRemaining = oTime;
      lastUpdateTime = Date.now();
    }
  }

  async function tryJoinGame() {
    if (!player?.name) return false;
    
    try {
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: $playerId,
          player_name: player.name
        })
      });
      if (response.ok) {
        return true;
      }
    } catch (error) {
      console.error('Error joining game:', error);
    }
    return false;
  }

  async function fetchGameState() {
    try {
      const response = await fetch(`${API_BASE_URL}/games/${gameId}`);
      const data = await response.json();
      
      // Store previous state to detect changes
      const hadPlayerO = playerO !== null;
      
      // Update game state
      boards = data.boards;
      metaBoard = data.meta_board;
      currentPlayer = data.current_player;
      winner = data.winner;
      gameOver = data.game_over;
      gameName = data.name;
      playerX = data.player_x.id;
      playerO = data.player_o.id;
      nextBoard = data.next_board;
      gameStarted = data.game_started;
      
      // Determine if we need to fetch opponent data
      const needToFetchOpponent = (!opponent && (playerX || playerO)) || (!hadPlayerO && playerO) || gameOver;
      
      // Fetch opponent stats when needed
      if (needToFetchOpponent) {
        updatePollingInterval();
        const opponentId = $playerId === playerX ? playerO : playerX;
        if (opponentId) {
          try {
            const response = await fetch(`${API_BASE_URL}/players/${opponentId}`);
            opponent = await response.json();
          } catch (error) {
            console.error('Error fetching opponent data:', error);
          }
        }
      }
      
      // Check if second player just joined
      if (playerO && !gameStarted && !showStartGameModal && !startGameModalShown) {
        showStartGameModal = true;
        startGameModalShown = true; // Mark that we've shown the modal
      }
      
      // Update server times
      updateTimesFromServer(data.player_x.time_remaining, data.player_o.time_remaining);
      
      isPlayer = false;
      playerSymbol = null;

      if (data.player_x.id === $playerId) {
        isPlayer = true;
        playerSymbol = "X";
      } else if (data.player_o.id === $playerId) {
        isPlayer = true;
        playerSymbol = "O";
      } else if (!hasTriedToJoin && !data.player_o.id && !gameOver && player?.name) {
        hasTriedToJoin = true;
        const joined = await tryJoinGame();
        if (joined) {
          await fetchGameState();
          return;
        }
      }

      gameUrl = window.location.origin + `/game/${gameId}`;
    } catch (error) {
      console.error('Error fetching game state:', error);
    }
  }

  async function makeMove(boardIndex, position) {
    if (!isMyTurn || gameOver) return;
    if (nextBoard !== null && nextBoard !== boardIndex) return;
    if (metaBoard[boardIndex] !== "") return;
    
    try {
      stopWarningCountdown();  // Reset warning countdown when making a move
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/move/${boardIndex}/${position}?player_id=${$playerId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      const data = await response.json();
      updateGameState(data);
      lastUpdateTime = Date.now();  // Reset the inactivity timer
    } catch (error) {
      console.error('Error making move:', error);
    }
  }

  function isBoardPlayable(boardIndex) {
    return (nextBoard === null || nextBoard === boardIndex) && 
           metaBoard[boardIndex] === "" &&
           !isBoardFull(boardIndex);
  }

  function isBoardFull(boardIndex) {
    return !boards[boardIndex].includes("");
  }

  function getBoardClass(boardIndex) {
    let classes = ['small-board'];
    if (isBoardPlayable(boardIndex)) classes.push('playable');
    if (nextBoard === boardIndex) classes.push('active');
    if (metaBoard[boardIndex]) classes.push('completed');
    return classes.join(' ');
  }

  function copyGameUrl() {
    navigator.clipboard.writeText(gameUrl);
    showCopiedMessage = true;
    setTimeout(() => {
      showCopiedMessage = false;
    }, 2000);
  }

  onMount(async () => {
    await fetchPlayerData();
    await fetchGameState();
    
    // Start with slower polling while waiting for opponent
    pollInterval = setInterval(fetchGameState, 3000);
  });

  onDestroy(() => {
    clearInterval(pollInterval);
    if (timeUpdateInterval) {
      clearInterval(timeUpdateInterval);
    }
    clearInterval(warningInterval);
  });

  function startWarningCountdown() {
    if (!warningInterval && isMyTurn) {
      warningCountdown = 10;  // 10 seconds to make a move
      warningInterval = setInterval(() => {
        warningCountdown--;
        if (warningCountdown <= 0) {
          resignGame();
          clearInterval(warningInterval);
          warningInterval = null;
        }
      }, 1000);
    }
  }

  function stopWarningCountdown() {
    if (warningInterval) {
      clearInterval(warningInterval);
      warningInterval = null;
      warningCountdown = null;
    }
  }

  async function resignGame() {
    try {
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/resign?player_id=${$playerId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        updateGameState(data);
      }
    } catch (error) {
      console.error('Error resigning game:', error);
    }
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function updateGameState(data) {
    boards = data.boards;
    metaBoard = data.meta_board;
    currentPlayer = data.current_player;
    nextBoard = data.next_board;
    winner = data.winner;
    gameOver = data.game_over;
    playerX = data.player_x.id;
    playerO = data.player_o.id;
    gameStarted = data.game_started;
    
    // Update server times
    updateTimesFromServer(data.player_x.time_remaining, data.player_o.time_remaining);

    if (gameOver) {
      // Only show the modal if it hasn't been dismissed yet
      if (!gameEndModalDismissed) {
        showGameEndModal = true;
      }
      clearInterval(pollInterval);
      clearInterval(timeUpdateInterval);
      clearInterval(warningInterval);
    } else {
      // Reset the dismissed flag when a new game starts
      gameEndModalDismissed = false;
      
      // Reset the start game modal flag if the game is completely reset
      if (!data.game_started && !data.player_o.id) {
        startGameModalShown = false;
      }
    }
  }

  async function handleGameStart() {
    if (playerSymbol === 'X') {
      // Only player X sends the start game API call
      try {
        const response = await fetch(`${API_BASE_URL}/games/${gameId}/start?player_id=${$playerId}`, {
          method: 'POST'
        });
        
        if (response.ok) {
          const data = await response.json();
          showStartGameModal = false;
          gameStarted = true;
          updateGameState(data);
        }
      } catch (error) {
        console.error('Error starting game:', error);
      }
    } else {
      // Player O just updates their local state
      showStartGameModal = false;
      gameStarted = true;
    }
  }

  function dismissGameEndModal() {
    showGameEndModal = false;
    gameEndModalDismissed = true;
  }

  // Add this function to update polling frequency
  function updatePollingInterval() {
    // Clear existing interval
    if (pollInterval) {
      clearInterval(pollInterval);
    }
    
    // Poll every second during active games, every 3 seconds while waiting
    const interval = (playerO && !gameOver) ? 1000 : 3000;
    pollInterval = setInterval(fetchGameState, interval);
  }
</script>

{#if isLoading}
  <div class="loading">Loading...</div>
{:else if !player?.name}
  <PlayerNameModal />
{:else}
<main>
  <h1>{gameName}</h1>
  
  <div class="game-info">
    <button class="share" on:click={copyGameUrl}>
      {showCopiedMessage ? 'URL Copied!' : 'Share Game URL'}
    </button>
    <button class="home" on:click={() => navigate('/')}>Back to Home</button>
    {#if isPlayer && !gameOver && playerO}
      <div class="resign-container">
        {#if showResignConfirm}
          <div class="resign-confirm">
            <span>Resign game?</span>
            <div class="resign-buttons">
              <button class="confirm" on:click={() => {
                resignGame();
                showResignConfirm = false;
              }}>Yes</button>
              <button class="cancel" on:click={() => showResignConfirm = false}>No</button>
            </div>
          </div>
        {:else}
          <button class="resign" on:click={() => showResignConfirm = true}>Resign Game</button>
        {/if}
      </div>
    {/if}
  </div>

  <div class="players">
    <div class="player player-x">
      <strong>Player X:</strong> {playerX ? (playerSymbol === 'X' ? player.name : opponent?.name) || 'Waiting...' : 'Waiting...'}
      {#if playerX}
        <div class="player-stats">
          {#if playerSymbol === 'X'}
            <span>Wins: {player.wins}</span>
            <span>Win Rate: {calculateWinRate(player)}%</span>
          {:else if opponent}
            <span>Wins: {opponent.wins || 0}</span>
            <span>Win Rate: {calculateWinRate(opponent)}%</span>
          {/if}
        </div>
      {/if}
    </div>
    <div class="player player-o">
      <strong>Player O:</strong> {playerO ? (playerSymbol === 'O' ? player.name : opponent?.name) || 'Waiting...' : 'Waiting...'}
      {#if playerO}
        <div class="player-stats">
          {#if playerSymbol === 'O'}
            <span>Wins: {player.wins}</span>
            <span>Win Rate: {calculateWinRate(player)}%</span>
          {:else if opponent}
            <span>Wins: {opponent.wins || 0}</span>
            <span>Win Rate: {calculateWinRate(opponent)}%</span>
          {/if}
        </div>
      {/if}
    </div>
  </div>

  <div class="time-display">
    {#if gameStarted}
      <div class="player x">X Time: {formatTime(displayedXTimeRemaining)}</div>
      <div class="player o">O Time: {formatTime(displayedOTimeRemaining)}</div>
    {:else}
      <div class="player x">X Time: 6:00</div>
      <div class="player o">O Time: 6:00</div>
    {/if}
  </div>

  {#if showWarning}
    <div class="time-warning">
      {#if warningCountdown !== null}
        Warning: Please a move in {warningCountdown} seconds or you will forfeit the game
      {/if}
    </div>
  {/if}

  <div class="status">
    {#if winner}
      Winner: {winner === 'X' ? (playerSymbol === 'X' ? player.name : opponent?.name) : (playerSymbol === 'O' ? player.name : opponent?.name)}!
    {:else if gameOver}
      Game Over - Draw!
    {:else if !isPlayer}
      {#if currentPlayer === "X" && !playerO}
        Waiting for player O to join...
      {:else}
        Spectating - {currentPlayer === 'X' ? (playerSymbol === 'X' ? player.name : opponent?.name) : (playerSymbol === 'O' ? player.name : opponent?.name)}'s turn
      {/if}
    {:else if !playerO}
      Waiting for another player to join...
    {:else if currentPlayer === playerSymbol}
      Your turn ({playerSymbol})
      {#if nextBoard !== null}
        - Must play in board {nextBoard + 1}
      {:else}
        - You can play in any available board
      {/if}
    {:else}
      Waiting for {currentPlayer === 'X' ? (playerSymbol === 'X' ? player.name : opponent?.name) : (playerSymbol === 'O' ? player.name : opponent?.name)} to move...
    {/if}
  </div>

  <div class="super-board {winner ? winner.toLowerCase() : ''}">
    {#each Array(9) as _, boardIndex}
      <div class={getBoardClass(boardIndex)}>
        {#if metaBoard[boardIndex]}
          <div class="board-winner {metaBoard[boardIndex].toLowerCase()}">
            {metaBoard[boardIndex] === 'T' ? 'Tie' : metaBoard[boardIndex]}
          </div>
        {:else}
          {#each boards[boardIndex] as cell, position}
            <button 
              class="cell {cell.toLowerCase()}" 
              on:click={() => makeMove(boardIndex, position)}
              disabled={!isPlayer || currentPlayer !== playerSymbol || cell || !isBoardPlayable(boardIndex)}
            >
              {cell}
            </button>
          {/each}
        {/if}
      </div>
    {/each}
  </div>

  {#if showStartGameModal}
    <StartGameModal
      playerXName={playerX ? (playerSymbol === 'X' ? player.name : opponent?.name) : 'Unknown'}
      playerOName={playerO ? (playerSymbol === 'O' ? player.name : opponent?.name) : 'Unknown'}
      playerXStats={$playerId === playerX ? player : opponent}
      playerOStats={$playerId === playerO ? player : opponent}
      on:start={handleGameStart}
    />
  {/if}

  {#if showGameEndModal}
    <GameEndModal
      isWinner={winner === playerSymbol}
      isDraw={gameOver && !winner}
      playerName={player.name}
      stats={player}
      on:dismiss={dismissGameEndModal}
    />
  {/if}
</main>
{/if}

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

  .game-info {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .players {
    display: flex;
    justify-content: space-around;
    width: 100%;
    max-width: 400px;
    margin-bottom: 2rem;
  }

  .player {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    background: #f5f5f5;
  }

  .player-x {
    color: #4CAF50;  /* Green for X */
  }

  .player-o {
    color: #2196F3;  /* Blue for O */
  }

  .player-stats {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: #666;
    display: flex;
    gap: 1rem;
  }

  .status {
    margin-bottom: 2rem;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .super-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 2rem;
    padding: 20px;
    background: #f0f0f0;
    border-radius: 8px;
    border: 3px solid #9e9e9e;  /* Default gray border */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);  /* Nice shadow for meta board */
    width: 500px;
    height: 500px;
    box-sizing: border-box;
  }

  /* Add winner colors for meta board */
  .super-board.x {
    border-color: #2e7d32;  /* Darker green for X winner */
    box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
  }

  .super-board.o {
    border-color: #1565c0;  /* Darker blue for O winner */
    box-shadow: 0 4px 12px rgba(21, 101, 192, 0.2);
  }

  .small-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 4px;
    padding: 8px;
    background: #f5f5f5;
    border-radius: 4px;
    transition: all 0.3s ease;
    opacity: 0.5;
    cursor: not-allowed;
    position: relative;
    border: 2px solid #9e9e9e;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);  /* Subtle shadow for all boards */
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    min-width: 120px;
    min-height: 120px;
  }

  .small-board.playable {
    background: #fff;
    opacity: 1;
    border-color: #757575;  /* Darker gray for playable boards */
    cursor: pointer;
  }

  .small-board.active {
    background: #fff;
    opacity: 1;
    border-color: #424242;  /* Even darker gray for active board */
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% { box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
    50% { box-shadow: 0 0 15px rgba(0, 0, 0, 0.2); }
    100% { box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
  }

  .small-board.completed {
    opacity: 1;
    cursor: not-allowed;
  }

  .small-board.completed .cell {
    background: #e0e0e0;  /* Darker background for cells in completed boards */
    border-color: #bdbdbd;
  }

  .board-winner {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 4rem;
    font-weight: bold;
    text-align: center;
    border-radius: 4px;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
  }

  .board-winner.x {
    color: #2e7d32;  /* Darker green */
    background: rgba(76, 175, 80, 0.15);
    border: 3px solid #2e7d32;
  }

  .board-winner.o {
    color: #1565c0;  /* Darker blue */
    background: rgba(33, 150, 243, 0.15);
    border: 3px solid #1565c0;
  }

  .board-winner.t {
    color: #424242;  /* Darker gray */
    background: rgba(117, 117, 117, 0.15);
    border: 3px solid #424242;
  }

  .cell {
    width: 100%;
    height: 100%;
    min-width: 30px;
    min-height: 30px;
    font-size: 1.2rem;
    font-weight: bold;
    border: 1px solid #ccc;
    background: white;
    transition: all 0.2s;
    color: #757575;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;
    line-height: 1;
    box-sizing: border-box;
  }

  .cell:disabled {
    cursor: not-allowed;
    background: #e0e0e0;  /* Darker background for disabled cells */
  }

  .cell:not(:disabled) {
    cursor: pointer;
  }

  .cell.x {
    color: #2e7d32;  /* Darker green */
    border-color: rgba(46, 125, 50, 0.3);
  }

  .cell.o {
    color: #1565c0;  /* Darker blue */
    border-color: rgba(21, 101, 192, 0.3);
  }

  .cell:not(:disabled):hover {
    background-color: #f0f0f0;
    transform: scale(1.05);
  }

  button {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .share {
    background-color: #2196F3;
    color: white;
  }

  .share:hover {
    background-color: #1976D2;
  }

  .home {
    background-color: #757575;
    color: white;
  }

  .home:hover {
    background-color: #616161;
  }

  .resign {
    background-color: #f44336;
    color: white;
  }

  .resign:hover {
    background-color: #d32f2f;
  }

  .time-display {
    font-size: 1.2rem;
    margin: 10px 0;
    display: flex;
    justify-content: space-between;
  }

  .time-warning {
    color: red;
    font-weight: bold;
    animation: pulse 1s infinite;
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-size: 1.2rem;
    color: #666;
  }

  .resign-container {
    height: 42px; /* Match the height of the standard buttons */
    display: flex;
    align-items: center;
  }

  .resign {
    background-color: #f44336;
    color: white;
    height: 100%;
  }

  .resign:hover {
    background-color: #d32f2f;
  }

  .resign-confirm {
    display: flex;
    flex-direction: row;
    align-items: center;
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 0 0.75rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    height: 100%;
  }

  .resign-confirm span {
    font-weight: bold;
    color: #333;
    margin-right: 0.75rem;
    white-space: nowrap;
  }

  .resign-buttons {
    display: flex;
    gap: 0.5rem;
  }

  .resign-buttons button {
    padding: 0.25rem 0.75rem;
    font-size: 0.9rem;
    min-width: 40px;
  }

  .confirm {
    background-color: #f44336;
    color: white;
  }

  .confirm:hover {
    background-color: #d32f2f;
  }

  .cancel {
    background-color: #9e9e9e;
    color: white;
  }

  .cancel:hover {
    background-color: #757575;
  }
</style> 