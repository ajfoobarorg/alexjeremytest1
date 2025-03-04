import { writable } from 'svelte/store';

// Generate a random player ID if not already stored
const storedPlayerId = localStorage.getItem('playerId') || 
                      Math.random().toString(36).substring(2, 15);
localStorage.setItem('playerId', storedPlayerId);

// Get player name from storage or set to null
const storedPlayerName = localStorage.getItem('playerName');

// Get player stats from storage or set defaults
const storedStats = JSON.parse(localStorage.getItem('playerStats')) || {
  wins: 0,
  losses: 0,
  draws: 0,
  totalGames: 0
};

export const playerId = writable(storedPlayerId);
export const playerName = writable(storedPlayerName);
export const playerStats = writable(storedStats);

// Save player name to localStorage when it changes
playerName.subscribe(value => {
  if (value) {
    localStorage.setItem('playerName', value);
  }
});

// Save player stats to localStorage when they change
playerStats.subscribe(value => {
  localStorage.setItem('playerStats', JSON.stringify(value));
});

// Function to update stats after a game
export function updatePlayerStats(result) {
  playerStats.update(stats => {
    const newStats = { ...stats, totalGames: stats.totalGames + 1 };
    if (result === 'win') newStats.wins = stats.wins + 1;
    else if (result === 'loss') newStats.losses = stats.losses + 1;
    else if (result === 'draw') newStats.draws = stats.draws + 1;
    return newStats;
  });
} 