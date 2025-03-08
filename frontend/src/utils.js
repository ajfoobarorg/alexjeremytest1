/**
 * Utility functions for the Ultimate Tic-Tac-Toe game
 */

/**
 * Calculate the total number of games played by a player
 * @param {Object} playerData - Player data object containing wins, losses, and draws
 * @returns {number} Total number of games played
 */
export function calculateTotalGames(playerData) {
  if (!playerData) return 0;
  return playerData.wins + playerData.losses + playerData.draws;
}

/**
 * Calculate the win rate percentage for a player
 * @param {Object} playerData - Player data object containing wins, losses, and draws
 * @returns {string} Win rate as a formatted percentage string with one decimal place
 */
export function calculateWinRate(playerData) {
  if (!playerData) return '0.0';
  const totalGames = calculateTotalGames(playerData);
  if (totalGames === 0) return '0.0';
  return (playerData.wins / totalGames * 100).toFixed(1);
} 