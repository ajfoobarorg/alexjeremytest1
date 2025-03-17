<script>
  import { onMount } from 'svelte';
  import { currentPath } from './router.js';
  import { isAuthenticated } from './stores.js';
  import Layout from './Layout.svelte';
  import Home from './Home.svelte';
  import Login from './Login.svelte';
  import Signup from './Signup.svelte';
  import Game from './Game.svelte';
  import Profile from './Profile.svelte';

  // Protected routes that require login
  const protectedRoutes = ['/game', '/profile'];

  // Route guard
  $: if ($currentPath && protectedRoutes.some(route => $currentPath.startsWith(route)) && !$isAuthenticated) {
    currentPath.set('/login');
  }

  // Route component mapping
  $: component = getRouteComponent($currentPath);
  $: componentProps = getRouteProps($currentPath);

  function getRouteComponent(path) {
    if (path === '/') return Home;
    if (path === '/login') return Login;
    if (path === '/signup') return Signup;
    if (path === '/profile') return Profile;
    if (path.startsWith('/game/')) return Game;
    return Home; // Default to home for unknown routes
  }

  function getRouteProps(path) {
    if (path.startsWith('/game/')) {
      return { gameId: path.split('/game/')[1] };
    }
    return {};
  }
</script>

<Layout currentPath={$currentPath}>
  {#if component === Game}
    <svelte:component this={component} gameId={componentProps.gameId} />
  {:else}
    <svelte:component this={component} />
  {/if}
</Layout>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
    background: #fafafa;
  }

  :global(*) {
    box-sizing: border-box;
  }
</style> 