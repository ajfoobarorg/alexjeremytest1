import { writable } from 'svelte/store';

// Generate a random player ID if not already stored
const storedPlayerId = localStorage.getItem('playerId') || 
                      Math.random().toString(36).substring(2, 15);
localStorage.setItem('playerId', storedPlayerId);

// Get player name from storage or set to null
const storedPlayerName = localStorage.getItem('playerName');

export const playerId = writable(storedPlayerId);
export const playerName = writable(storedPlayerName);

// Save player name to localStorage when it changes
playerName.subscribe(value => {
  if (value) {
    localStorage.setItem('playerName', value);
  }
}); 