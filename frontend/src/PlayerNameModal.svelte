# This is a new file
<script>
  import { playerId } from './stores.js';
  import { API_BASE_URL } from './config.js';

  let name = '';
  let error = '';

  async function handleSubmit() {
    if (name.trim().length < 2) {
      error = 'Name must be at least 2 characters long';
      return;
    }

    try {
      // Update player name in the backend
      const response = await fetch(`${API_BASE_URL}/players/${$playerId}/name`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: name.trim() })
      });

      if (!response.ok) {
        throw new Error('Failed to save player name');
      }

      // Force a page reload to update all components with the new name
      window.location.reload();
    } catch (error) {
      console.error('Error saving player name:', error);
      error = 'Failed to save name. Please try again.';
    }
  }
</script>

<div class="modal-backdrop">
  <div class="modal">
    <h2>Welcome to Tic Tac Toe!</h2>
    <p>Please enter your name to continue:</p>
    
    {#if error}
      <p class="error">{error}</p>
    {/if}

    <form on:submit|preventDefault={handleSubmit}>
      <input
        type="text"
        bind:value={name}
        placeholder="Your name"
        autofocus
      />
      <button type="submit">Continue</button>
    </form>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    max-width: 400px;
    width: 90%;
  }

  h2 {
    margin: 0 0 1rem 0;
    color: #333;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  input {
    padding: 0.8rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  button {
    padding: 0.8rem;
    font-size: 1rem;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  button:hover {
    background: #45a049;
  }

  .error {
    color: #f44336;
    margin: 0.5rem 0;
  }
</style> 