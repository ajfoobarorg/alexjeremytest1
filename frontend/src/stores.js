import { writable } from 'svelte/store';

// Generate a unique player ID with timestamp to ensure uniqueness
function generatePlayerId() {
  return Math.random().toString(36).substring(2, 12) + '_' + Date.now();
}

// Use sessionStorage instead of localStorage
let storedPlayerId;
let storedPlayerName;
let storedPlayerStats;

// Check if we're in a browser environment
if (typeof window !== 'undefined') {
  storedPlayerId = sessionStorage.getItem('playerId') || generatePlayerId();
  storedPlayerName = sessionStorage.getItem('playerName') || '';
  storedPlayerStats = JSON.parse(sessionStorage.getItem('playerStats') || '{"wins": 0, "losses": 0, "draws": 0}');
  
  // Save to sessionStorage
  sessionStorage.setItem('playerId', storedPlayerId);
} else {
  // Default values for SSR
  storedPlayerId = generatePlayerId();
  storedPlayerName = '';
  storedPlayerStats = {"wins": 0, "losses": 0, "draws": 0};
}

export const playerId = writable(storedPlayerId);
export const playerName = writable(storedPlayerName);
export const playerStats = writable(storedPlayerStats);

// Subscribe to changes and update sessionStorage
playerId.subscribe(value => {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('playerId', value);
  }
});

// Save player name to localStorage when it changes
playerName.subscribe(value => {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('playerName', value);
  }
});

// Save player stats to localStorage when they change
playerStats.subscribe(value => {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('playerStats', JSON.stringify(value));
  }
});

// Function to update stats after a game
export function updatePlayerStats(result) {
  playerStats.update(stats => {
    if (result === 'win') stats.wins++;
    else if (result === 'loss') stats.losses++;
    else if (result === 'draw') stats.draws++;
    return stats;
  });
} 