# Create new file
<script>
  import { onMount } from 'svelte';
  import { myPlayerData, authLoading } from './stores.js';
  import { API_BASE_URL } from './config.js';
  import { COUNTRIES, TIMEZONE_GROUPS } from './constants.js';

  // Create maps for easy lookup
  const countryCodeToName = new Map(COUNTRIES.map(c => [c.code, c.name]));
  const countryNameToCode = new Map(COUNTRIES.map(c => [c.name, c.code]));

  let profile = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    location: '',
    country: '',
    timezone: '',
    stats: {
      wins: 0,
      losses: 0,
      draws: 0,
      elo: 0
    }
  };

  // Display value for country (full name)
  let displayCountry = '';

  let error = '';
  let success = '';
  let isLoading = false;

  onMount(async () => {
    if (!$authLoading && $myPlayerData) {
      await loadProfile();
    }
  });

  $: if (!$authLoading && $myPlayerData) {
    loadProfile();
  }

  async function loadProfile() {
    try {
      const response = await fetch(`${API_BASE_URL}/profile/${$myPlayerData.id}`);
      if (response.ok) {
        profile = await response.json();
        // Set initial display value for country
        displayCountry = profile.country ? countryCodeToName.get(profile.country) || '' : '';
      } else {
        error = 'Failed to load profile';
      }
    } catch (err) {
      error = 'An error occurred while loading profile';
      console.error('Profile load error:', err);
    }
  }

  function handleCountryInput(event) {
    const value = event.target.value;
    // Check if the value matches a country name
    if (countryNameToCode.has(value)) {
      profile.country = countryNameToCode.get(value);
      displayCountry = value;
    }
    // If not a full country name, just update display value
    else {
      displayCountry = value;
    }
  }

  async function handleSubmit() {
    // Validate country before submitting
    if (displayCountry && !profile.country) {
      error = 'Please select a valid country from the list';
      return;
    }

    isLoading = true;
    error = '';
    success = '';

    try {
      const response = await fetch(`${API_BASE_URL}/profile/${$myPlayerData.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: profile.username,
          email: profile.email,
          first_name: profile.first_name,
          last_name: profile.last_name,
          location: profile.location,
          country: profile.country,
          timezone: profile.timezone
        })
      });

      const data = await response.json();

      if (response.ok) {
        success = 'Profile updated successfully';
        profile = data;
        // Update display country after successful save
        displayCountry = profile.country ? countryCodeToName.get(profile.country) || '' : '';
      } else {
        error = data.detail || 'Failed to update profile';
      }
    } catch (err) {
      error = 'An error occurred while updating profile';
      console.error('Profile update error:', err);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="profile-container">
  <h1>Profile Settings</h1>

  <div class="stats-section">
    <h2>Game Statistics</h2>
    <div class="stats-grid">
      <div class="stat-item">
        <label>Wins</label>
        <span>{profile.stats.wins}</span>
      </div>
      <div class="stat-item">
        <label>Losses</label>
        <span>{profile.stats.losses}</span>
      </div>
      <div class="stat-item">
        <label>Draws</label>
        <span>{profile.stats.draws}</span>
      </div>
      <div class="stat-item">
        <label>ELO Rating</label>
        <span>{profile.stats.elo}</span>
      </div>
    </div>
  </div>

  <form on:submit|preventDefault={handleSubmit}>
    {#if error}
      <div class="error">{error}</div>
    {/if}
    {#if success}
      <div class="success">{success}</div>
    {/if}

    <div class="form-grid">
      <div class="form-group">
        <label for="username">Username</label>
        <input
          type="text"
          id="username"
          bind:value={profile.username}
          required
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input
          type="email"
          id="email"
          bind:value={profile.email}
          required
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="first_name">First Name</label>
        <input
          type="text"
          id="first_name"
          bind:value={profile.first_name}
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="last_name">Last Name</label>
        <input
          type="text"
          id="last_name"
          bind:value={profile.last_name}
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="location">Location</label>
        <input
          type="text"
          id="location"
          bind:value={profile.location}
          placeholder="City, State"
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="country">Country</label>
        <input
          type="text"
          id="country"
          list="country-list"
          bind:value={displayCountry}
          on:input={handleCountryInput}
          placeholder="Start typing a country name..."
          disabled={isLoading}
        />
        <datalist id="country-list">
          {#each COUNTRIES.sort((a, b) => a.name.localeCompare(b.name)) as country}
            <option value={country.name}/>
          {/each}
        </datalist>
      </div>

      <div class="form-group">
        <label for="timezone">Timezone</label>
        <input
          type="text"
          id="timezone"
          list="timezone-list"
          bind:value={profile.timezone}
          placeholder="Start typing a timezone..."
          disabled={isLoading}
        />
        <datalist id="timezone-list">
          {#each Object.entries(TIMEZONE_GROUPS) as [group, timezones]}
            {#each timezones as tz}
              <option value={tz.value} label={tz.label}/>
            {/each}
          {/each}
        </datalist>
      </div>
    </div>

    <button type="submit" class="save-btn" disabled={isLoading}>
      {isLoading ? 'Saving...' : 'Save Changes'}
    </button>
  </form>
</div>

<style>
  .profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1 {
    color: #333;
    margin-bottom: 2rem;
  }

  .stats-section {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  h2 {
    color: #555;
    font-size: 1.2rem;
    margin-bottom: 1rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
  }

  .stat-item {
    text-align: center;
  }

  .stat-item label {
    display: block;
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 0.3rem;
  }

  .stat-item span {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2e7d32;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1rem;
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

  .save-btn {
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

  .save-btn:hover {
    background: #1b5e20;
  }

  .save-btn:disabled {
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

  .success {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 0.8rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
</style> 