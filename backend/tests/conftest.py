import pytest
import os
import tempfile
import datetime
import json
from peewee import SqliteDatabase
from models import db, Player, Game

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