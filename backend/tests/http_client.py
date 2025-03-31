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
        import sys
        self.port = server_port or self._find_free_port()
        # Get Python executable info for debugging
        py_executable = sys.executable
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        logger.info(f"Python executable: {py_executable}, version: {py_version}")
        
        # Use sys.executable to get the exact Python interpreter that's running the test
        python_cmd = py_executable  # Use the detected executable
        logger.info(f"Using Python interpreter: {python_cmd}")
        self.server_command = f"{python_cmd} -m uvicorn main:app --port {self.port} --host 0.0.0.0 --log-level debug --reload"
        self.server_url = f"http://localhost:{self.port}"
        self.process = None
        self.log_file = None
        
        # Print DEBUG information about environment
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Environment variables: PATH={os.environ.get('PATH')}")
        logger.info(f"Python path: {sys.path}")
        
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
        
        # Test if python3 is available - this helps debug GitHub Actions issues
        try:
            test_result = subprocess.run(
                "which python3", 
                shell=True, 
                capture_output=True, 
                text=True,
                check=True
            )
            logger.info(f"python3 found at: {test_result.stdout.strip()}")
            
            # Also check version
            test_result = subprocess.run(
                "python3 --version", 
                shell=True, 
                capture_output=True, 
                text=True,
                check=True
            )
            logger.info(f"python3 version: {test_result.stdout.strip()}")
            
            # Check if uvicorn is installed
            test_result = subprocess.run(
                "python3 -m pip list | grep uvicorn", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            logger.info(f"uvicorn package: {test_result.stdout.strip() if test_result.returncode == 0 else 'Not found'}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking python3: {str(e)}")
            logger.error(f"stdout: {e.stdout}, stderr: {e.stderr}")
        
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
                    
                    # Flush the log file and reopen for reading
                    if self.log_file:
                        self.log_file.flush()
                    
                    # Try to read the log file for error details
                    try:
                        # Close and reopen to ensure we get the latest content
                        if self.log_file:
                            self.log_file.close()
                            self.log_file = open('backend_server.log', 'a')
                            
                        with open('backend_server.log', 'r') as f:
                            log_content = f.read()
                            # Print the entire log to console
                            print("\n\n==== SERVER LOG START ====")
                            print(log_content)
                            print("==== SERVER LOG END ====\n\n")
                            logger.error(f"Full server log:\n{log_content}")
                    except Exception as log_e:
                        logger.error(f"Failed to read log file: {str(log_e)}")
                    
                    raise Exception(f"Server process exited prematurely with code {returncode}")
            
            logger.info(f"Waiting for server to start (attempt {i+1}/{max_retries})...")
            
            # Every 5 attempts, check if the port is being listened on
            if i % 5 == 0:
                try:
                    # Check port status using different commands depending on OS
                    if os.name != 'nt':  # Unix/Linux/macOS
                        # Try netstat first
                        ns_cmd = f"netstat -tuln | grep {self.port}"
                        netstat_result = subprocess.run(
                            ns_cmd, 
                            shell=True, 
                            capture_output=True, 
                            text=True
                        )
                        if netstat_result.returncode == 0:
                            logger.info(f"Port {self.port} status: {netstat_result.stdout.strip()}")
                        else:
                            # Try ss if netstat fails
                            ss_cmd = f"ss -tuln | grep {self.port}"
                            ss_result = subprocess.run(
                                ss_cmd, 
                                shell=True, 
                                capture_output=True, 
                                text=True
                            )
                            logger.info(f"Port {self.port} status: {ss_result.stdout.strip() if ss_result.returncode == 0 else 'Not found'}")
                    else:
                        # Windows
                        netstat_result = subprocess.run(
                            f"netstat -an | findstr {self.port}", 
                            shell=True, 
                            capture_output=True, 
                            text=True
                        )
                        logger.info(f"Port {self.port} status: {netstat_result.stdout.strip() if netstat_result.returncode == 0 else 'Not found'}")
                except Exception as e:
                    logger.error(f"Error checking port status: {str(e)}")
                
                # Check if the server process is still running
                if self.process and self.process.poll() is not None:
                    logger.error(f"Server process exited with code {self.process.poll()}")
                    
                    # Display log content
                    if self.log_file:
                        self.log_file.flush()
                        
                    try:
                        with open('backend_server.log', 'r') as f:
                            log_content = f.read()
                            print("\n\n==== SERVER LOG START ====")
                            print(log_content)
                            print("==== SERVER LOG END ====\n\n")
                    except Exception as log_e:
                        logger.error(f"Failed to read log file: {str(log_e)}")
            
            time.sleep(retry_interval)
            
        # If we got here, server didn't start in time
        logger.error("Server startup timed out. Checking server log...")
        
        # Flush and close the log file
        if self.log_file:
            self.log_file.flush()
            self.log_file.close()
            self.log_file = None
        
        # Try to read log file for error details
        try:
            with open('backend_server.log', 'r') as f:
                log_content = f.read()
                # Print the entire log to console
                print("\n\n==== SERVER LOG START ====")
                print(log_content)
                print("==== SERVER LOG END ====\n\n")
                logger.error(f"Server log:\n{log_content}")
        except Exception as e:
            logger.error(f"Failed to read log file: {str(e)}")
        
        # Print the process state
        if self.process:
            print(f"Process state: {self.process.poll()}")
            
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