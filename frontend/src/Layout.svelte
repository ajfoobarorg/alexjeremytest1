<script>
  import { onMount } from 'svelte';
  import { navigate } from './router.js';
  import { myPlayerData, isAuthenticated, logout } from './stores.js';
  import { API_BASE_URL } from './config.js';

  export let currentPath;
  
  let isMobileMenuOpen = false;
  let windowWidth;

  // Close mobile menu when route changes
  $: if (currentPath) {
    isMobileMenuOpen = false;
  }

  // Responsive breakpoint
  $: isDesktop = windowWidth >= 768;

  async function handleLogout() {
    await logout();
    navigate('/');
  }
</script>

<svelte:window bind:innerWidth={windowWidth}/>

<div class="app-container">
  {#if !isDesktop}
    <nav class="top-nav">
      <button class="hamburger" on:click={() => isMobileMenuOpen = !isMobileMenuOpen}>
        <span></span>
        <span></span>
        <span></span>
      </button>
      <div class="site-title">Ultimate TTT</div>
      {#if !$isAuthenticated}
        <div class="auth-buttons">
          <button class="sign-up-btn-small" on:click={() => navigate('/signup')}>Sign Up</button>
          <button class="login-btn-small" on:click={() => navigate('/login')}>Log In</button>
        </div>
      {/if}
    </nav>
  {/if}

  {#if isDesktop || isMobileMenuOpen}
    <nav class="left-nav" class:mobile={!isDesktop}>
      <div class="nav-header">
        <h1>Ultimate TTT</h1>
        {#if !isDesktop}
          <button class="close-nav" on:click={() => isMobileMenuOpen = false}>×</button>
        {/if}
      </div>

      <div class="nav-links">
        <a 
          href="/" 
          class:active={currentPath === '/'} 
          on:click|preventDefault={() => navigate('/')}
        >
          Play
        </a>
        <a 
          href="/learn" 
          class:active={currentPath === '/learn'} 
          on:click|preventDefault={() => navigate('/learn')}
        >
          Learn
        </a>
      </div>

      <div class="nav-footer">
        {#if $isAuthenticated}
          <a 
            href="/profile" 
            class="profile-btn" 
            class:active={currentPath === '/profile'} 
            on:click|preventDefault={() => navigate('/profile')}
          >
            Profile Settings
          </a>
          <button class="logout-btn" on:click={handleLogout}>Log Out</button>
        {:else}
          <button class="sign-up-btn" on:click={() => navigate('/signup')}>Sign Up</button>
          <button class="login-btn" on:click={() => navigate('/login')}>Log In</button>
        {/if}
      </div>
    </nav>
  {/if}

  <main class="content">
    <slot></slot>
  </main>
</div>

<style>
  .app-container {
    display: flex;
    min-height: 100vh;
  }

  .left-nav {
    width: 240px;
    background: #fff;
    border-right: 1px solid #e0e0e0;
    display: flex;
    flex-direction: column;
    padding: 1.5rem;
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
  }

  .left-nav.mobile {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.98);
    z-index: 1000;
  }

  .nav-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .nav-header h1 {
    font-size: 1.5rem;
    color: #333;
    margin: 0;
  }

  .close-nav {
    background: none;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    padding: 0.5rem;
    color: #666;
  }

  .nav-links {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links a {
    color: #333;
    text-decoration: none;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .nav-links a:hover {
    background-color: #f5f5f5;
  }

  .nav-links a.active {
    background-color: #e8f5e9;
    color: #2e7d32;
  }

  .nav-footer {
    margin-top: auto;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .top-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: #fff;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
    padding: 0 1rem;
    z-index: 90;
  }

  .hamburger {
    background: none;
    border: none;
    padding: 0.5rem;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .hamburger span {
    display: block;
    width: 24px;
    height: 2px;
    background: #333;
  }

  .site-title {
    margin-left: 1rem;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .auth-buttons {
    margin-left: auto;
    display: flex;
    gap: 0.5rem;
  }

  .content {
    flex: 1;
    margin-left: 240px;
    padding: 2rem;
  }

  @media (max-width: 767px) {
    .content {
      margin-left: 0;
      padding-top: calc(60px + 1rem);
    }
  }

  /* Button Styles */
  .sign-up-btn, .sign-up-btn-small {
    background: #2e7d32;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }

  .sign-up-btn-small {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .login-btn, .login-btn-small {
    background: #1976d2;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }

  .login-btn-small {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .logout-btn {
    background: #f5f5f5;
    color: #666;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }

  button:hover {
    opacity: 0.9;
  }

  .profile-btn {
    display: block;
    width: 100%;
    padding: 0.8rem;
    background: #f5f5f5;
    color: #333;
    border: none;
    border-radius: 4px;
    text-align: center;
    text-decoration: none;
    margin-bottom: 0.5rem;
    transition: background-color 0.2s;
  }

  .profile-btn:hover {
    background: #e0e0e0;
  }

  .profile-btn.active {
    background: #e8f5e9;
    color: #2e7d32;
  }
</style> 