import pytest
import os
import logging
import tempfile
import datetime
import json
from peewee import SqliteDatabase
from models import db, Player, Game

logger = logging.getLogger(__name__)

@pytest.fixture
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
def sample_players(test_db):
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

@pytest.fixture
def http_client(real_backend_server):
    """Create a real HTTP client for tests against a running server."""
    from tests.http_client import ApiClient
    print(f"\n🌐 Creating HTTP client for real server testing on port {real_backend_server.port}...")
    return ApiClient(real_backend_server.server_url)