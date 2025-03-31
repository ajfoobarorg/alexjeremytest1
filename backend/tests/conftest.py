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
    
    # Close the current connection if open
    if not db.is_closed():
        db.close()
    
    # Set up the test database
    test_db = SqliteDatabase(test_db_path)
    db.bind([Player, Game], bind_refs=False, bind_backrefs=False)
    db.connect()
    
    # Drop tables if they exist and create new ones
    db.drop_tables([Player, Game], safe=True)
    db.create_tables([Player, Game])
    
    # Return None since we don't need to use the fixture value
    yield None
    
    # Cleanup after test
    if not db.is_closed():
        db.close()
    
    # Restore the original database
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
def backend_server():
    """Start a backend server for true HTTP testing.
    
    Note: Only use this fixture if you want to test against a real server.
    For normal tests, the TestClient is faster and more convenient.
    """
    # Comment out the server start code to use the TestClient by default
    # Uncomment this section to start a real server
    """
    from tests.http_client import start_server_thread
    server = start_server_thread()
    yield server
    # Server will be stopped by atexit handler
    """
    
    # For now, we're just yielding None to indicate no real server
    yield None

@pytest.fixture
def api_client(backend_server):
    """Create an API client for HTTP-based tests.
    
    When backend_server is None (default), this creates a client that uses
    the FastAPI TestClient. When a real server is started, this creates
    a client that makes real HTTP requests.
    """
    # If we're using a real server, create a real HTTP client
    if backend_server:
        from tests.http_client import ApiClient
        return ApiClient(backend_server.server_url)
    
    # Otherwise, create a wrapper around the TestClient
    # that has the same interface as ApiClient
    from fastapi.testclient import TestClient
    from main import app
    
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
            """Create a game directly (test helper)."""
            # Since we're in-process, we can create a Game object directly
            # This wouldn't be possible with a real HTTP client
            player_x = Player.get(Player.id == player_x_id)
            player_o = Player.get(Player.id == player_o_id)
            game = Game.create(
                player_x=player_x,
                player_o=player_o,
                current_player="X",
                last_move_time=datetime.datetime.now(),
                started=True
            )
            return game
        
        def resign_game(self, game_id, player_id):
            return self.client.post(f"/games/{game_id}/resign?player_id={player_id}")
    
    return TestClientWrapper() 