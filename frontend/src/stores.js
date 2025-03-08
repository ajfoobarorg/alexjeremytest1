import { writable } from 'svelte/store';
import { API_BASE_URL } from './config.js';

// Generate a unique player ID with timestamp to ensure uniqueness
function generatePlayerId() {
  return Math.random().toString(36).substring(2, 12) + '_' + Date.now();
}

// Cookie helper functions
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function setCookie(name, value, days = 365) {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = `expires=${date.toUTCString()}`;
  document.cookie = `${name}=${value};${expires};path=/;SameSite=Strict`;
}

// Get or create player ID from cookie
let storedPlayerId;

// Check if we're in a browser environment
if (typeof window !== 'undefined') {
  storedPlayerId = getCookie('playerId') || generatePlayerId();
  // Save to cookie if it's new
  if (!getCookie('playerId')) {
    setCookie('playerId', storedPlayerId);
  }
} else {
  // Default value for SSR
  storedPlayerId = generatePlayerId();
}

export const playerId = writable(storedPlayerId);

// Subscribe to changes and update cookie
playerId.subscribe(value => {
  if (typeof window !== 'undefined') {
    setCookie('playerId', value);
  }
}); 