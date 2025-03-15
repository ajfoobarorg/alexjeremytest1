import { writable, derived } from 'svelte/store';
import { API_BASE_URL } from './config.js';

// Create stores
export const isLoggedIn = writable(false);
export const myPlayerData = writable(null);
export const playerId = writable(null);
export const authLoading = writable(false);

// Function to check login status and fetch current player data
export async function checkLoginStatus() {
  authLoading.set(true);
  try {
    const response = await fetch(`${API_BASE_URL}/profile/me`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json'
      }
    });
    if (response.ok) {
      const data = await response.json();
      myPlayerData.set(data);
      playerId.set(data.id);
      isLoggedIn.set(true);
    } else {
      myPlayerData.set(null);
      playerId.set(null);
      isLoggedIn.set(false);
    }
  } catch (error) {
    console.error('Error checking login status:', error);
    myPlayerData.set(null);
    playerId.set(null);
    isLoggedIn.set(false);
  } finally {
    authLoading.set(false);
  }
}

// Initialize by checking login status
if (typeof window !== 'undefined') {
  checkLoginStatus();
}

export async function logout() {
  try {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });
  } finally {
    // Clear stores regardless of server response
    isLoggedIn.set(false);
    myPlayerData.set(null);
    playerId.set(null);
  }
}

export const isAuthenticated = derived(
  [isLoggedIn, authLoading],
  ([$isLoggedIn, $authLoading]) => $isLoggedIn && !$authLoading
);

export function requireAuth(callback) {
  return derived(
    [isAuthenticated, authLoading],
    ([$isAuthenticated, $authLoading]) => {
      if (!$authLoading && !$isAuthenticated) {
        navigate('/login');
      } else if (!$authLoading && $isAuthenticated) {
        callback();
      }
    }
  );
}

// Initialize from localStorage if available
const storedId = localStorage.getItem('playerId');
if (storedId) {
  playerId.set(storedId);
}

// Subscribe to changes and update localStorage
playerId.subscribe(value => {
  if (value) {
    localStorage.setItem('playerId', value);
  } else {
    localStorage.removeItem('playerId');
  }
});