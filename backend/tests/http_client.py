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
    
    def __init__(self, server_port=None):
        self.port = server_port or self._find_free_port()
        self.server_command = f"python -m uvicorn main:app --port {self.port} --host 0.0.0.0"
        self.server_url = f"http://localhost:{self.port}"
        self.process = None
        self.log_file = None
        
    def _find_free_port(self):
        """Find a free port to use for the server."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def start(self):
        """Start the backend server."""
        # Start the server as a subprocess
        logger.info(f"Starting backend server with command: {self.server_command}")
        
        # Use different process group handling based on platform
        kwargs = {}
        if os.name != 'nt':  # Unix/Linux/macOS
            kwargs['preexec_fn'] = os.setsid  # Use process group for clean termination
        
        # Get the current directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info(f"Starting server in directory: {current_dir}")
        
        # Set up log file for server output
        self.log_file = open('backend_server.log', 'w')
        logger.info(f"Server output will be logged to backend_server.log")
        
        self.process = subprocess.Popen(
            self.server_command, 
            shell=True,
            cwd=current_dir,
            stdout=self.log_file,
            stderr=self.log_file,
            **kwargs
        )
        
        # Wait for server to become available
        max_retries = 60  # Increase max retries for GitHub Actions
        retry_interval = 2  # Longer interval between retries
        for i in range(max_retries):
            try:
                logger.info(f"Checking server health at {self.server_url}/health")
                response = requests.get(f"{self.server_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("Backend server is up and running")
                    return
                else:
                    logger.warning(f"Server returned status code {response.status_code}")
            except requests.RequestException as e:
                logger.warning(f"Health check failed: {str(e)}")
                
                # Check if process is still running
                if self.process.poll() is not None:
                    returncode = self.process.poll()
                    logger.error(f"Server process exited with code {returncode}")
                    
                    # Try to read the log file for error details
                    try:
                        with open('backend_server.log', 'r') as f:
                            log_tail = ''.join(f.readlines()[-20:])  # Last 20 lines
                            logger.error(f"Server log tail:\n{log_tail}")
                    except Exception as log_e:
                        logger.error(f"Failed to read log file: {str(log_e)}")
                    
                    raise Exception(f"Server process exited prematurely with code {returncode}")
            
            logger.info(f"Waiting for server to start (attempt {i+1}/{max_retries})...")
            time.sleep(retry_interval)
            
        # If we got here, server didn't start in time
        logger.error("Server startup timed out. Checking server log...")
        
        # Try to read log file for error details
        try:
            with open('backend_server.log', 'r') as f:
                log_content = f.read()
                logger.error(f"Server log:\n{log_content}")
        except Exception as e:
            logger.error(f"Failed to read log file: {str(e)}")
            
        raise Exception("Failed to start backend server after maximum retries")

    def stop(self):
        """Stop the backend server."""
        if self.process:
            print("🛑 Stopping backend server...")
            
            try:
                if os.name != 'nt':  # Unix/Linux/macOS
                    # Kill the entire process group
                    try:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                        self.process.wait(timeout=5)
                    except:
                        # If anything goes wrong, try SIGKILL
                        try:
                            os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                        except:
                            pass
                else:
                    # Windows - terminate directly
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except:
                # Last resort: terminate process
                try:
                    self.process.kill()
                except:
                    pass
                    
            self.process = None
            
            # Close log file if it's open
            if self.log_file:
                try:
                    self.log_file.close()
                except:
                    pass
                self.log_file = None


# Singleton server instance to ensure we only start one server
_server_instance = None

def get_server():
    """Get the backend server instance (singleton)."""
    global _server_instance
    if _server_instance is None:
        # Use environment port if specified, otherwise dynamic
        server_port = os.environ.get("BACKEND_PORT")
        if server_port:
            server_port = int(server_port)
        _server_instance = BackendServer(server_port)
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
    logger.info("Waiting for server to start in thread...")
    time.sleep(10)  # Increase wait time for GitHub Actions
    
    return server