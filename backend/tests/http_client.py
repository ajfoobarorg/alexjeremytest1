import requests
import subprocess
import time
import logging
import os
import signal
import threading
import atexit

logger = logging.getLogger(__name__)

class ApiClient:
    """HTTP client for interacting with the backend API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def signup(self, user_data):
        """Create a new user."""
        return self.session.post(f"{self.base_url}/auth/signup", json=user_data)
    
    def login(self, email):
        """Log in a user."""
        return self.session.post(f"{self.base_url}/auth/login", json={"email": email})
    
    def logout(self):
        """Log out the current user."""
        return self.session.post(f"{self.base_url}/auth/logout")
    
    def get_profile(self, player_id):
        """Get a player's profile."""
        return self.session.get(f"{self.base_url}/profile/{player_id}")
    
    def get_stats(self):
        """Get site statistics."""
        return self.session.get(f"{self.base_url}/stats")
    
    def get_game(self, game_id):
        """Get a game's details."""
        return self.session.get(f"{self.base_url}/games/{game_id}")
    
    def make_move(self, game_id, board_index, position, player_id):
        """Make a move in a game."""
        return self.session.post(
            f"{self.base_url}/games/{game_id}/move/{board_index}/{position}?player_id={player_id}"
        )
    
    def create_game(self, player_x_id, player_o_id):
        """Create a new game between two players."""
        # This endpoint might not exist in the current API
        # It's included for completeness in case it's added later
        return self.session.post(
            f"{self.base_url}/games/create",
            json={"player_x_id": player_x_id, "player_o_id": player_o_id}
        )
    
    def direct_game_creation(self, player_x_id, player_o_id):
        """Create a game through the matchmaking system.
        
        For the HTTP client, we don't have access to the database directly,
        so we use the matchmaking system to create a game, like a real frontend client would.
        """
        # First try the direct API endpoint
        response = self.create_game(player_x_id, player_o_id)
        if response.status_code == 200:
            return response.json()
            
        print("No direct games/create endpoint available. Using matchmaking system...")
        import time
        
        # Have both players join matchmaking
        response = self.session.post(
            f"{self.base_url}/matchmaking/join",
            json={"player_id": player_x_id}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to add first player to matchmaking: {response.status_code}")
            
        response = self.session.post(
            f"{self.base_url}/matchmaking/join", 
            json={"player_id": player_o_id}
        )
        if response.status_code != 200:
            # Cancel first player to clean up
            self.session.post(f"{self.base_url}/matchmaking/cancel", json={"player_id": player_x_id})
            raise Exception(f"Failed to add second player to matchmaking: {response.status_code}")
        
        # Poll for match with first player
        game_id = None
        for _ in range(10):  # Try 10 times
            response = self.session.post(
                f"{self.base_url}/matchmaking/ping",
                json={"player_id": player_x_id}
            )
            if response.status_code != 200:
                continue
                
            data = response.json()
            if data["status"] == "waiting_acceptance" or data["status"] == "matched":
                # Also ping with second player to accept match
                self.session.post(
                    f"{self.base_url}/matchmaking/ping",
                    json={"player_id": player_o_id}
                )
                
            if data["status"] == "matched" and data["game_id"]:
                game_id = data["game_id"]
                break
                
            time.sleep(0.5)
            
        if not game_id:
            # Cancel both players to clean up
            self.session.post(f"{self.base_url}/matchmaking/cancel", json={"player_id": player_x_id})
            self.session.post(f"{self.base_url}/matchmaking/cancel", json={"player_id": player_o_id})
            raise Exception("Failed to create game through matchmaking after 10 attempts")
            
        # Get the game details to find out which player is X
        response = self.session.get(f"{self.base_url}/games/{game_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to get game details: {response.status_code}")
            
        # Find out who is player X in this game
        game_details = response.json()
        actual_player_x_id = game_details["player_x"]["id"]
            
        # Mark the game as ready - must be done by the actual player X
        response = self.session.post(f"{self.base_url}/games/{game_id}/ready?player_id={actual_player_x_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to mark game as ready: {response.status_code}")
            
        # Return game info in the same format as the create_game endpoint would
        return {"id": game_id}
    
    def resign_game(self, game_id, player_id):
        """Resign from a game."""
        return self.session.post(f"{self.base_url}/games/{game_id}/resign?player_id={player_id}")


class BackendServer:
    """Server manager for starting and stopping the backend server."""
    
    def __init__(self, server_command="cd /Users/aroetter/src/alexjeremytest1/backend && python -m uvicorn main:app --reload", 
                 server_url="http://localhost:8000"):
        self.server_command = server_command
        self.server_url = server_url
        self.process = None

    def start(self):
        """Start the backend server."""
        # Start the server as a subprocess
        logger.info(f"Starting backend server with command: {self.server_command}")
        self.process = subprocess.Popen(
            self.server_command, 
            shell=True,
            preexec_fn=os.setsid  # Use process group for clean termination
        )
        
        # Wait for server to become available
        max_retries = 30
        retry_interval = 1
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.server_url}/health")
                if response.status_code == 200:
                    logger.info("Backend server is up and running")
                    return
            except requests.RequestException:
                pass
            
            logger.info(f"Waiting for server to start (attempt {i+1}/{max_retries})...")
            time.sleep(retry_interval)
            
        raise Exception("Failed to start backend server")

    def stop(self):
        """Stop the backend server."""
        if self.process:
            logger.info("Stopping backend server")
            # Kill the entire process group
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait()
            self.process = None


# Singleton server instance to ensure we only start one server
_server_instance = None

def get_server():
    """Get the backend server instance (singleton)."""
    global _server_instance
    if _server_instance is None:
        server_command = os.environ.get(
            "BACKEND_SERVER_COMMAND", 
            "cd /Users/aroetter/src/alexjeremytest1/backend && python -m uvicorn main:app --reload"
        )
        server_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
        _server_instance = BackendServer(server_command, server_url)
    return _server_instance

def start_server_thread():
    """Start the server in a background thread."""
    server = get_server()
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Register shutdown
    atexit.register(server.stop)
    
    # Wait for server to start
    time.sleep(5)
    
    return server