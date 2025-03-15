<script>
  import { navigate } from './router.js';
  import { checkLoginStatus, authLoading, isAuthenticated } from './stores.js';
  import { API_BASE_URL } from './config.js';
  import { onMount } from 'svelte';
  import { COUNTRIES, TIMEZONES, TIMEZONE_GROUPS } from './constants.js';

  let username = '';
  let email = '';
  let level = '0';
  let detectedTimezone = '';
  let country = '';
  let error = '';
  let isLoading = false;

  const PLAYER_LEVELS = [
    { value: '0', label: 'New to the game' },
    { value: '1', label: 'Beginner' },
    { value: '2', label: 'Intermediate' },
    { value: '3', label: 'Advanced' }
  ];

  onMount(() => {
    // If user is already authenticated, redirect to home
    if (!$authLoading && $isAuthenticated) {
      navigate('/');
      return;
    }

    if ($authLoading) return;

    try {
      // Get the IANA timezone name from the browser
      detectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      console.log('Detected IANA timezone:', detectedTimezone);
      
      // Try to detect country using Intl.DateTimeFormat
      try {
        const timeFormat = new Intl.DateTimeFormat();
        const resolvedLocale = timeFormat.resolvedOptions().locale;
        const countryCode = resolvedLocale.split('-')[1]?.toUpperCase();
        
        // Verify it's a valid country code
        if (countryCode && COUNTRIES.some(c => c.code === countryCode)) {
          country = countryCode;
        } else {
          // Fallback: try to get country from browser language
          const browserLang = navigator.language || navigator.userLanguage;
          const langCountryCode = browserLang.split('-')[1]?.toUpperCase();
          if (langCountryCode && COUNTRIES.some(c => c.code === langCountryCode)) {
            country = langCountryCode;
          }
        }
      } catch (err) {
        console.error('Failed to detect country:', err);
      }
    } catch (err) {
      console.error('Failed to detect timezone:', err);
    }
  });

  // Reactive statement to handle auth state changes
  $: if (!$authLoading && $isAuthenticated) {
    navigate('/');
  }

  async function handleSubmit() {
    error = '';
    isLoading = true;

    if (!username || !email || !level) {
      error = 'Please fill in all required fields';
      isLoading = false;
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          username,
          email,
          level,
          timezone: detectedTimezone || null,
          country: country || null
        }),
      });

      if (response.ok) {
        await checkLoginStatus();  // This will update stores based on the cookie
        navigate('/');
      } else {
        const data = await response.json();
        error = data.detail;
      }
    } catch (err) {
      error = 'An error occurred during signup';
      console.error('Signup error:', err);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="signup-container">
  <h1>Create Account</h1>
  
  <form on:submit|preventDefault={handleSubmit}>
    {#if error}
      <div class="error">{error}</div>
    {/if}

    <div class="form-group">
      <label for="username">Username</label>
      <input
        type="text"
        id="username"
        bind:value={username}
        required
        disabled={isLoading}
      />
    </div>

    <div class="form-group">
      <label for="email">Email</label>
      <input
        type="email"
        id="email"
        bind:value={email}
        required
        disabled={isLoading}
      />
    </div>

    <div class="form-group">
      <label for="level">Experience Level</label>
      <select
        id="level"
        bind:value={level}
        required
        disabled={isLoading}
      >
        {#each PLAYER_LEVELS as { value, label }}
          <option {value}>{label}</option>
        {/each}
      </select>
    </div>

    <button type="submit" disabled={isLoading}>
      {isLoading ? 'Creating Account...' : 'Create Account'}
    </button>

    <div class="login-prompt">
      <p>Already have an account?</p>
      <button type="button" class="login-link" on:click={() => navigate('/login')}>
        Log in
      </button>
    </div>
  </form>
</div>

<style>
  .signup-container {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #555;
  }

  input, select {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  input:focus, select:focus {
    outline: none;
    border-color: #2e7d32;
    box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.2);
  }

  .signup-btn {
    width: 100%;
    padding: 1rem;
    background: #2e7d32;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .signup-btn:hover {
    background: #1b5e20;
  }

  .signup-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .error {
    background: #ffebee;
    color: #c62828;
    padding: 0.8rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .login-prompt {
    margin-top: 2rem;
    text-align: center;
  }

  .login-prompt p {
    margin: 0 0 0.5rem 0;
    color: #666;
  }

  .login-link {
    background: none;
    border: none;
    color: #1976d2;
    font-weight: bold;
    cursor: pointer;
    padding: 0;
  }

  .login-link:hover {
    text-decoration: underline;
  }
</style> 