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