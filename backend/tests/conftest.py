import pytest
import os
import tempfile
import datetime
import json
import logging
from peewee import SqliteDatabase
from models import db, Player, Game

logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def test_db():
    """Create a test database and tables for each test."""
    # Create a temporary database file
    test_db_fd, test_db_path = tempfile.mkstemp()
    
    # Store the original database
    original_db = db.database
    
    # Force close any existing connections (main app might have initialized it)
    for _ in range(3):  # Try multiple times to ensure it's closed
        try:
            if not db.is_closed():
                db.close()
        except:
            pass
    
    # Set up the test database
    test_db = SqliteDatabase(test_db_path)
    # Replace the database in the db instance
    db._Database__database = test_db
    db.bind([Player, Game], bind_refs=False, bind_backrefs=False)
    
    try:
        db.connect(reuse_if_open=True)
    except:
        # If connection fails, try one more time after forcing a close
        if not db.is_closed():
            db.close()
        db.connect()
    
    # Drop tables if they exist and create new ones
    db.drop_tables([Player, Game], safe=True)
    db.create_tables([Player, Game])
    
    # Return None since we don't need to use the fixture value
    yield None
    
    # Cleanup after test
    try:
        if not db.is_closed():
            db.close()
    except:
        pass
    
    # Restore the original database connection
    db._Database__database = original_db
    db.bind([Player, Game], bind_refs=False, bind_backrefs=False)
    
    os.close(test_db_fd)
    os.unlink(test_db_path)

@pytest.fixture
def sample_players():
    """Create sample players for testing."""
    players = []
    for i in range(3):
        player = Player.create(
            username=f"test_player_{i}",
            email=f"player{i}@test.com",
            elo=1000 + i*100
        )
        players.append(player)
    return players

@pytest.fixture
def active_game(sample_players):
    """Create an active game between two players."""
    game = Game.create(
        player_x=sample_players[0],
        player_o=sample_players[1],
        current_player="X",
        next_board=4  # Center board
    )
    return game

@pytest.fixture
def completed_game(sample_players):
    """Create a completed game with a winner."""
    # Create a game where X wins by taking the center column of the meta board
    boards = [[""]*9 for _ in range(9)]
    
    # Set up winning condition in boards 1, 4, 7 (center column)
    for board_idx in [1, 4, 7]:
        # X wins each board with a diagonal
        boards[board_idx][0] = "X"
        boards[board_idx][4] = "X"
        boards[board_idx][8] = "X"
    
    game = Game.create(
        player_x=sample_players[0],
        player_o=sample_players[1],
        current_player="O",  # Last move was by X
        game_over=True,
        winner="X",
        boards=json.dumps(boards),
        completed_at=datetime.datetime.now()
    )
    return game

@pytest.fixture(scope="session")
def real_backend_server():
    """Start a real backend server for HTTP-based testing.
    
    This fixture starts an actual server process for true end-to-end testing.
    """
    from tests.http_client import start_server_thread
    print("\n⚡ Starting real HTTP server for end-to-end testing...")
    server = start_server_thread()
    yield server
    print("\n🛑 Stopping real HTTP server...")
    # Server will be stopped by atexit handler


@pytest.fixture(scope="session")
def no_backend_server():
    """Dummy fixture that doesn't start a backend server.
    
    This is used when we want to test with the TestClient instead.
    """
    yield None

@pytest.fixture
def http_client(real_backend_server):
    """Create a real HTTP client for tests against a running server."""
    from tests.http_client import ApiClient
    print(f"\n🌐 Creating HTTP client for real server testing on port {real_backend_server.port}...")
    return ApiClient(real_backend_server.server_url)

@pytest.fixture
def test_client(no_backend_server, monkeypatch):
    """Create a TestClient wrapper for in-process testing."""
    # Patch initialize_db function to avoid re-initializing the database
    import sys
    import models
    
    # Save the original initialize_db function
    original_initialize_db = models.initialize_db
    
    # Replace it with a no-op function
    def mock_initialize_db():
        pass
    
    # Apply the patch
    monkeypatch.setattr(models, "initialize_db", mock_initialize_db)
    
    # Now import the app (which would normally call initialize_db on import)
    from fastapi.testclient import TestClient
    
    # Force reload the main module to pick up our patch
    if "main" in sys.modules:
        del sys.modules["main"]
    
    from main import app
    
    print("\n🔍 Creating TestClient for in-process testing...")
    test_client = TestClient(app)
    
    class TestClientWrapper:
        def __init__(self):
            self.client = test_client
            
        def signup(self, user_data):
            return self.client.post("/auth/signup", json=user_data)
        
        def login(self, email):
            return self.client.post("/auth/login", json={"email": email})
        
        def logout(self):
            return self.client.post("/auth/logout")
        
        def get_profile(self, player_id):
            return self.client.get(f"/profile/{player_id}")
        
        def get_stats(self):
            return self.client.get("/stats")
        
        def get_game(self, game_id):
            return self.client.get(f"/games/{game_id}")
        
        def make_move(self, game_id, board_index, position, player_id):
            return self.client.post(
                f"/games/{game_id}/move/{board_index}/{position}?player_id={player_id}"
            )
        
        def create_game(self, player_x_id, player_o_id):
            # This endpoint might not exist, but included for completeness
            return self.client.post(
                "/games/create",
                json={"player_x_id": player_x_id, "player_o_id": player_o_id}
            )
        
        def direct_game_creation(self, player_x_id, player_o_id):
            """Create a game through matchmaking like a real client would.
            
            This method creates a game using the matchmaking API, just like
            the frontend would, without any direct database access.
            """
            print("Creating game through matchmaking system...")
            import time
            
            # Have both players join matchmaking
            response = self.client.post(
                "/matchmaking/join",
                json={"player_id": player_x_id}
            )
            if response.status_code != 200:
                raise Exception(f"Failed to add first player to matchmaking: {response.status_code}")
                
            response = self.client.post(
                "/matchmaking/join", 
                json={"player_id": player_o_id}
            )
            if response.status_code != 200:
                # Cancel first player to clean up
                self.client.post("/matchmaking/cancel", json={"player_id": player_x_id})
                raise Exception(f"Failed to add second player to matchmaking: {response.status_code}")
            
            # Poll for match with first player
            game_id = None
            for _ in range(10):  # Try 10 times
                response = self.client.post(
                    "/matchmaking/ping",
                    json={"player_id": player_x_id}
                )
                if response.status_code != 200:
                    continue
                    
                data = response.json()
                if data["status"] == "waiting_acceptance" or data["status"] == "matched":
                    # Also ping with second player to accept match
                    self.client.post(
                        "/matchmaking/ping",
                        json={"player_id": player_o_id}
                    )
                    
                if data["status"] == "matched" and data["game_id"]:
                    game_id = data["game_id"]
                    break
                    
                time.sleep(0.5)
                
            if not game_id:
                # Cancel both players to clean up
                self.client.post("/matchmaking/cancel", json={"player_id": player_x_id})
                self.client.post("/matchmaking/cancel", json={"player_id": player_o_id})
                raise Exception("Failed to create game through matchmaking after 10 attempts")
                
            # Get the game details to find out which player is X
            response = self.client.get(f"/games/{game_id}")
            if response.status_code != 200:
                raise Exception(f"Failed to get game details: {response.status_code}")
                
            # Find out who is player X in this game
            game_details = response.json()
            actual_player_x_id = game_details["player_x"]["id"]
                
            # Mark the game as ready - must be done by the actual player X
            response = self.client.post(f"/games/{game_id}/ready?player_id={actual_player_x_id}")
            if response.status_code != 200:
                raise Exception(f"Failed to mark game as ready: {response.status_code}")
                
            # Return game info in the same format expected by the test
            return {"id": game_id}
        
        def resign_game(self, game_id, player_id):
            return self.client.post(f"/games/{game_id}/resign?player_id={player_id}")
    
    return TestClientWrapper()

# Keep the original api_client fixture for backward compatibility
@pytest.fixture
def api_client(test_client):
    """Create an API client for backward compatibility.
    
    This uses the TestClient by default to maintain compatibility with existing tests.
    """
    return test_client