<script>
  import { onMount, onDestroy } from 'svelte';
  import { playerId, authLoading, myPlayerData } from './stores.js';
  import { navigate } from './router.js';
  import GameEndModal from './GameEndModal.svelte';
  import { API_BASE_URL } from './config.js';
  import StartGameModal from './StartGameModal.svelte';
  import { calculateWinRate } from './utils.js';
  
  export let gameId;

  // Game state - single source of truth
  let game = null;
  
  // UI state
  let showGameEndModal = false;
  let gameEndModalDismissed = false;
  let showStartGameModal = true;  // Start true since we always show it at game start
  let isLoading = true;
  let showResignConfirm = false;
  let gameReady = false;  // Track if game has been marked as ready
  
  // Player information
  let playerSymbol = null;
  let opponentInfo = null;  // Only need to store opponent info

  // Timing variables
  let displayedXTimeRemaining = null;
  let displayedOTimeRemaining = null;
  let warningCountdown = null;
  let warningInterval;
  let pollInterval;
  let timeUpdateInterval;
  let lastPlayer = null;  // Track the last player to detect changes
  let lastTurnStartTime = null;  // Track when the current turn started

  // Track if we're currently handling a game end
  let handlingGameEnd = false;
  
  // Computed values from game state
  $: gameUrl = game ? window.location.origin + `/game/${game.id}` : window.location.href;
  $: playerX = game?.player_x?.id;
  $: playerO = game?.player_o?.id;
  $: isMyTurn = game?.current_player === 'X' ? playerX === $playerId : playerO === $playerId;
  $: timeRemaining = game?.current_player === 'X' ? displayedXTimeRemaining : displayedOTimeRemaining;
  $: showWarning = isMyTurn && !game?.game_over && (
    (timeRemaining !== null && timeRemaining <= 25) || // Low total time warning
    warningCountdown !== null // Inactivity warning
  );
  $: gameStarted = !showStartGameModal;  // Game has started when start modal is dismissed
  $: amIWinner = game?.winner ? (game.winner === playerSymbol) : false;

  async function fetchPlayerInfo(playerId) {
    try {
      const response = await fetch(`${API_BASE_URL}/profile/${playerId}`);
      if (!response.ok) {
        console.error('Failed to fetch player info');
        return null;
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching player info:', error);
      return null;
    }
  }

  async function updatePlayerInfo() {
    if (!game) return;
    
    // Determine opponent's ID
    const opponentId = playerSymbol === 'X' ? game.player_o.id : game.player_x.id;
    
    // Only fetch opponent info
    const oppInfo = await fetchPlayerInfo(opponentId);
    console.log("Opponenet info fetched:", oppInfo);
    opponentInfo = oppInfo;
  }

  async function fetchGameState() {
    try {
      const response = await fetch(`${API_BASE_URL}/games/${gameId}`);
      if (!response.ok) {
        // If game doesn't exist, redirect to home
        navigate('/');
        return;
      }
      const data = await response.json();
      
      // Store full game data
      game = data;
      
      // Set player symbol on first load
      if (!playerSymbol) {
        if (data.player_x.id === $playerId) {
          playerSymbol = "X";
        } else if (data.player_o.id === $playerId) {
          playerSymbol = "O";
        } else {
          // If not a player, redirect to home
          navigate('/');
          return;
        }
        
        // Fetch player info on first load
        await updatePlayerInfo();
      }
      
      // Update times
      updateTimesFromServer(data.player_x.time_remaining, data.player_o.time_remaining);
    } catch (error) {
      console.error('Error fetching game state:', error);
      navigate('/');
    }
  }

  // Function to handle game end
  async function handleGameEnd() {
    if (handlingGameEnd) return;
    handlingGameEnd = true;
    
    try {
      showGameEndModal = true;
    } finally {
      handlingGameEnd = false;
    }
  }

  // Show game end modal when game is over and we haven't dismissed it
  $: if (game?.game_over && !showGameEndModal && !gameEndModalDismissed && !handlingGameEnd) {
    handleGameEnd();
  }

  function updateDisplayTimes() {
    if (game?.game_over || !game?.started || showStartGameModal) {
      return;
    }
    
    // Decrement time for current player
    if (game.current_player === 'X') {
      displayedXTimeRemaining = Math.max(0, displayedXTimeRemaining - 1);
    } else if (game.current_player === 'O') {
      displayedOTimeRemaining = Math.max(0, displayedOTimeRemaining - 1);
    }
    
    // Start inactivity warning if it's been 10 seconds since turn started
    if (isMyTurn && !warningInterval && lastTurnStartTime && (Date.now() - lastTurnStartTime) >= 10000) {
      console.log('Starting warning countdown due to inactivity:', {
        now: Date.now(),
        lastTurnStartTime,
        diff: Date.now() - lastTurnStartTime
      });
      startWarningCountdown();
    }
  }

  function updateTimesFromServer(xTime, oTime) {
    // Always update initial times if they're null
    if (displayedXTimeRemaining === null || displayedOTimeRemaining === null) {
      console.log('Initializing times from server:', { xTime, oTime });
      displayedXTimeRemaining = xTime;
      displayedOTimeRemaining = oTime;
      lastPlayer = game?.current_player;
      
      // Initialize turn start time if it's our turn and game has started
      if (isMyTurn && game?.started && !showStartGameModal) {
        console.log('Setting initial lastTurnStartTime');
        lastTurnStartTime = Date.now();
      }
      return;
    }

    // Update times if the current player has changed
    if (game?.current_player !== lastPlayer) {
      console.log('Turn changed:', {
        from: lastPlayer,
        to: game?.current_player,
        xTime,
        oTime,
        started: game?.started,
        showStartModal: showStartGameModal,
        isMyTurn
      });
      displayedXTimeRemaining = xTime;
      displayedOTimeRemaining = oTime;
      lastPlayer = game?.current_player;
      
      // Reset and update turn start time if it's my turn and game has started
      if (isMyTurn && game?.started && !showStartGameModal) {
        console.log('Setting lastTurnStartTime on turn change');
        lastTurnStartTime = Date.now();
        stopWarningCountdown();  // Clear any existing warning
      } else {
        console.log('Clearing lastTurnStartTime (not my turn)');
        lastTurnStartTime = null; // Clear the turn start time when it's not our turn
        stopWarningCountdown();  // Make sure to clear any existing warning
      }
    } else if (isMyTurn && game?.started && !showStartGameModal && !lastTurnStartTime) {
      // Handle case where it's still our turn but lastTurnStartTime was cleared
      console.log('Resetting lastTurnStartTime for current turn');
      lastTurnStartTime = Date.now();
    }
  }

  async function makeMove(boardIndex, position) {
    if (!isMyTurn || game.game_over) return;
    if (game.next_board !== null && game.next_board !== boardIndex) return;
    if (game.meta_board[boardIndex] !== "") return;
    
    try {
      stopWarningCountdown();  // Reset warning countdown when making a move
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/move/${boardIndex}/${position}?player_id=${$playerId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      const data = await response.json();
      game = data; // Update game state directly
      
      // Update server times
      updateTimesFromServer(data.player_x.time_remaining, data.player_o.time_remaining);

      if (data.game_over && !gameEndModalDismissed) {
        // Game just ended - handle game end
        clearInterval(pollInterval);
        clearInterval(timeUpdateInterval);
        clearInterval(warningInterval);
        await handleGameEnd();
      }
    } catch (error) {
      console.error('Error making move:', error);
    }
  }

  function isBoardPlayable(boardIndex) {
    if (!game) return false;
    return (game.next_board === null || game.next_board === boardIndex) && 
           game.meta_board[boardIndex] === "" &&
           !isBoardFull(boardIndex);
  }

  function isBoardFull(boardIndex) {
    if (!game) return true;
    return !game.boards[boardIndex].includes("");
  }

  function getBoardClass(boardIndex) {
    let classes = ['small-board'];
    if (isBoardPlayable(boardIndex)) classes.push('playable');
    if (game?.next_board === boardIndex) classes.push('active');
    if (game?.meta_board[boardIndex]) classes.push('completed');
    return classes.join(' ');
  }

  onMount(async () => {
    // Wait for auth to finish loading and ensure we have a playerId
    if ($authLoading || !$playerId) {
      return;
    }
    
    // First fetch game state
    await fetchGameState();
    
    // Set up polling for game state
    pollInterval = setInterval(fetchGameState, 1000);
    
    // Set up time updates - run every second
    timeUpdateInterval = setInterval(updateDisplayTimes, 1000);
    
    // Mark loading as complete
    isLoading = false;
  });

  // Reactive statement to handle auth state changes
  $: if (!$authLoading) {
    if (!$playerId) {
      // Only navigate away if auth is done loading and we have no playerId
      navigate('/');
    }
  }

  onDestroy(() => {
    clearInterval(pollInterval);
    if (timeUpdateInterval) {
      clearInterval(timeUpdateInterval);
    }
    clearInterval(warningInterval);
  });

  function startWarningCountdown() {
    if (!warningInterval) {
      console.log('Starting warning countdown');
      warningCountdown = 10;  // 10 seconds to make a move
      warningInterval = setInterval(() => {
        warningCountdown--;
        if (warningCountdown <= 0) {
          console.log('Warning countdown reached zero, resigning game');
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
        game = data; // Update game state directly
        
        if (data.game_over && isMyTurn && !gameEndModalDismissed) {
          // Game just ended - handle game end
          clearInterval(pollInterval);
          clearInterval(timeUpdateInterval);
          clearInterval(warningInterval);
          await handleGameEnd();
        }
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

  async function handleGameStart() {
    showStartGameModal = false;
    
    // Only player X needs to signal they're ready to start
    if (playerSymbol === 'X') {
      try {
        const response = await fetch(`${API_BASE_URL}/games/${gameId}/ready?player_id=${$playerId}`, {
          method: 'POST'
        });
        
        if (response.ok) {
          const data = await response.json();
          game = data; // Update game state directly
          gameReady = true; // Mark game as ready to start timers
          
          // Initialize times from server and turn start time if it's our turn
          displayedXTimeRemaining = data.player_x.time_remaining;
          displayedOTimeRemaining = data.player_o.time_remaining;
          lastPlayer = data.current_player;
          console.log('Game started (X):', { 
            xTime: displayedXTimeRemaining, 
            oTime: displayedOTimeRemaining,
            currentPlayer: data.current_player,
            gameReady,
            started: data.started
          });
          if (isMyTurn) {
            lastTurnStartTime = Date.now();
          }
        }
      } catch (error) {
        console.error('Error starting game:', error);
      }
    } else {
      // For player O, we need to wait for the game state to show started
      console.log('Player O waiting for game to start...');
      const checkGameReady = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/games/${gameId}`);
          if (response.ok) {
            const data = await response.json();

            
            if (data.started) {
              clearInterval(checkGameReady);
              game = data;
              gameReady = true; // Mark game as ready to start timers
              
              // Initialize times from server and turn start time if it's our turn
              displayedXTimeRemaining = data.player_x.time_remaining;
              displayedOTimeRemaining = data.player_o.time_remaining;
              lastPlayer = data.current_player;
              console.log('Game started (O):', { 
                xTime: displayedXTimeRemaining, 
                oTime: displayedOTimeRemaining,
                currentPlayer: data.current_player,
                gameReady
              });
              if (isMyTurn) {
                lastTurnStartTime = Date.now();
              }
            }
          }
        } catch (error) {
          console.error('Error checking game ready state:', error);
        }
      }, 1000);
    }
  }

  function dismissGameEndModal() {
    showGameEndModal = false;
    gameEndModalDismissed = true;
  }

</script>

{#if isLoading}
  <div class="loading">Loading...</div>
{:else if game}
<main>
  <div class="game-info">
    {#if game.game_over}
      <button class="home" on:click={() => navigate('/')}>Back to Home</button>
      <button class="analyze" disabled>Analyze Moves</button>
    {:else}
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

  <div class="game-header" class:mobile-hidden={gameStarted && !game.game_over}>    
    <div class="players">
      <div class="player player-x">
        <strong>Player X:</strong> {playerX === $playerId ? $myPlayerData.username : opponentInfo?.username}
        <div class="player-stats">
          <span>ELO: {playerX === $playerId ? $myPlayerData.stats.elo : opponentInfo?.stats?.elo}</span>
          <span>Wins: {playerX === $playerId ? $myPlayerData.stats.wins : opponentInfo?.stats?.wins}</span>
          <span>Win Rate: {calculateWinRate(playerX === $playerId ? $myPlayerData.stats : opponentInfo?.stats)}%</span>
        </div>
      </div>
      <div class="player player-o">
        <strong>Player O:</strong> {playerO === $playerId ? $myPlayerData.username : opponentInfo?.username}
        <div class="player-stats">
          <span>ELO: {playerO === $playerId ? $myPlayerData.stats.elo : opponentInfo?.stats?.elo}</span>
          <span>Wins: {playerO === $playerId ? $myPlayerData.stats.wins : opponentInfo?.stats?.wins}</span>
          <span>Win Rate: {calculateWinRate(playerO === $playerId ? $myPlayerData.stats : opponentInfo?.stats)}%</span>
        </div>
      </div>
    </div>
  </div>

  <div class:game-active-view={gameStarted && !game.game_over}>
    <div class="time-display">
      {#if gameStarted}
        <div class="player x">X Time: {formatTime(displayedXTimeRemaining)}</div>
        <div class="player o">O Time: {formatTime(displayedOTimeRemaining)}</div>
      {:else}
        <div class="player x">X Time: 6:00</div>
        <div class="player o">O Time: 6:00</div>
      {/if}
    </div>

    <div class="status">
      {#if game.winner}
        Winner: {game.winner === 'X' ? $myPlayerData.username : opponentInfo?.username}!
      {:else if game.game_over}
        Game Over - Draw!
      {:else if game.current_player === playerSymbol}
        Your turn ({playerSymbol})
        {#if game.next_board !== null}
          - Must play in board {game.next_board + 1}
        {:else}
          - You can play in any available board
        {/if}
      {:else}
        Waiting for {game.current_player === 'X' ? $myPlayerData.username : opponentInfo?.username} to move...
      {/if}
    </div>

    {#if showWarning}
      <div class="time-warning">
        {#if warningCountdown !== null}
          Warning: Please make a move in {warningCountdown} seconds or you will forfeit the game!
        {:else}
          Warning: You have {timeRemaining} seconds remaining!
        {/if}
      </div>
    {/if}

    <div class="super-board {game.winner ? game.winner.toLowerCase() : ''}">
      {#each Array(9) as _, boardIndex}
        <div class={getBoardClass(boardIndex)}>
          {#if game.meta_board[boardIndex]}
            <div class="board-winner {game.meta_board[boardIndex].toLowerCase()}">
              {game.meta_board[boardIndex] === 'T' ? 'Tie' : game.meta_board[boardIndex]}
            </div>
          {:else}
            {#each game.boards[boardIndex] as cell, position}
              <button 
                class="cell {cell.toLowerCase()}" 
                on:click={() => makeMove(boardIndex, position)}
                disabled={!isMyTurn || game.current_player !== playerSymbol || cell || !isBoardPlayable(boardIndex)}
              >
                {cell}
              </button>
            {/each}
          {/if}
        </div>
      {/each}
    </div>
  </div>

  {#if showStartGameModal}
    <StartGameModal
      playerXName={playerX === $playerId ? $myPlayerData.username : opponentInfo?.username}
      playerOName={playerO === $playerId ? $myPlayerData.username : opponentInfo?.username}
      playerXStats={playerX === $playerId ? $myPlayerData.stats : opponentInfo?.stats}
      playerOStats={playerO === $playerId ? $myPlayerData.stats : opponentInfo?.stats}
      on:start={handleGameStart}
    />
  {/if}

  {#if showGameEndModal}
    <GameEndModal
      isWinner={amIWinner}
      isDraw={game.game_over && !game.winner}
      playerName={$myPlayerData.username}
      stats={$myPlayerData.stats}
      eloChange={playerSymbol === 'X' ? game.player_x.elo_change : game.player_o.elo_change}
      on:dismiss={dismissGameEndModal}
    />
  {/if}
</main>
{:else}
  <div class="loading">Loading game data...</div>
{/if}

<style>
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    font-family: Arial, sans-serif;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow-x: hidden;
  }

  h1 {
    color: #333;
    margin-bottom: 2rem;
    text-align: center;
    width: 100%;
    word-break: break-word;
  }

  .game-info {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    width: 100%;
    max-width: 500px;
  }

  .game-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 500px;
    margin-bottom: 1.5rem;
  }

  .hidden {
    display: none;
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
    width: 100%;
    max-width: 500px;
    height: auto;
    aspect-ratio: 1 / 1;
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
    color: #d32f2f;
    font-weight: bold;
    animation: pulse 1s infinite;
    background: #ffebee;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: 2px solid #d32f2f;
    margin: 1rem 0;
    text-align: center;
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

  /* Media queries for responsive design */
  @media (max-width: 600px) {
    main {
      padding: 0.75rem;
    }

    h1 {
      font-size: 1.5rem;
      margin-bottom: 0.75rem;
    }

    .game-info {
      margin-bottom: 0.5rem;
    }

    /* Hide game header during active gameplay on mobile */
    .mobile-hidden {
      display: none;
    }

    .super-board {
      gap: 10px;
      padding: 10px;
      margin-bottom: 1rem;
    }

    .small-board {
      min-width: 80px;
      min-height: 80px;
      padding: 4px;
      gap: 2px;
    }

    .board-winner {
      font-size: 2.5rem;
    }

    .cell {
      min-width: 20px;
      min-height: 20px;
      font-size: 1rem;
    }

    button {
      padding: 0.6rem 1rem;
      font-size: 0.9rem;
    }

    .game-info {
      gap: 0.5rem;
    }

    .players {
      flex-direction: column;
      gap: 0.5rem;
      align-items: center;
      margin-bottom: 1rem;
    }

    .time-display {
      width: 100%;
      justify-content: space-around;
      margin: 0.5rem 0;
      font-size: 1rem;
    }

    .status {
      font-size: 1rem;
      text-align: center;
      margin-bottom: 1rem;
    }

    /* Compact game view */
    .game-active-view {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
    }

    .game-active-view .time-display {
      order: 1;
      margin-bottom: 0.5rem;
    }

    .game-active-view .status {
      order: 2;
      margin-bottom: 0.5rem;
    }

    .game-active-view .super-board {
      order: 3;
    }

    .game-active-view .time-warning {
      order: 4;
      margin-top: 0.5rem;
    }
  }

  @media (max-width: 400px) {
    main {
      padding: 0.5rem;
    }

    .super-board {
      gap: 5px;
      padding: 5px;
    }

    .small-board {
      min-width: 60px;
      min-height: 60px;
      padding: 2px;
      gap: 1px;
    }

    .board-winner {
      font-size: 2rem;
    }

    .cell {
      min-width: 15px;
      min-height: 15px;
      font-size: 0.9rem;
    }

    button {
      padding: 0.5rem 0.8rem;
      font-size: 0.8rem;
    }

    .time-display {
      font-size: 0.9rem;
    }

    .status {
      font-size: 0.9rem;
    }
  }

  .analyze {
    background-color: #9C27B0;
    color: white;
  }

  .analyze:hover:not([disabled]) {
    background-color: #7B1FA2;
  }

  .analyze[disabled] {
    background-color: #E1BEE7;
    cursor: not-allowed;
    opacity: 0.7;
  }
</style> 