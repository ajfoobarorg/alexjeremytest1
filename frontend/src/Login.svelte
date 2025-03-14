<script>
  import { navigate } from './router.js';
  import { checkLoginStatus } from './stores.js';
  import { API_BASE_URL } from './config.js';

  let email = '';
  let error = '';
  let isLoading = false;

  async function handleSubmit() {
    if (!email) {
      error = 'Please enter your email address';
      return;
    }

    isLoading = true;
    error = '';

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        await checkLoginStatus();  // This will update stores based on the cookie
        navigate('/');
      } else {
        const data = await response.json();
        error = data.detail || 'Email not found. Please sign up first.';
      }
    } catch (err) {
      error = 'An error occurred. Please try again.';
      console.error('Login error:', err);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="login-container">
  <h1>Welcome Back!</h1>
  
  <form on:submit|preventDefault={handleSubmit}>
    {#if error}
      <div class="error">{error}</div>
    {/if}

    <div class="form-group">
      <label for="email">Email</label>
      <input
        type="email"
        id="email"
        bind:value={email}
        placeholder="Enter your email"
        required
        disabled={isLoading}
      />
    </div>

    <button type="submit" class="login-btn" disabled={isLoading}>
      {isLoading ? 'Logging in...' : 'Log In'}
    </button>

    <div class="signup-prompt">
      <p>Don't have an account?</p>
      <button type="button" class="signup-link" on:click={() => navigate('/signup')}>
        Sign up
      </button>
    </div>
  </form>
</div>

<style>
  .login-container {
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

  input {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  input:focus {
    outline: none;
    border-color: #1976d2;
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
  }

  .login-btn {
    width: 100%;
    padding: 1rem;
    background: #1976d2;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .login-btn:hover {
    background: #1565c0;
  }

  .login-btn:disabled {
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

  .signup-prompt {
    margin-top: 2rem;
    text-align: center;
  }

  .signup-prompt p {
    margin: 0 0 0.5rem 0;
    color: #666;
  }

  .signup-link {
    background: none;
    border: none;
    color: #1976d2;
    font-weight: bold;
    cursor: pointer;
    padding: 0;
  }

  .signup-link:hover {
    text-decoration: underline;
  }
</style> 