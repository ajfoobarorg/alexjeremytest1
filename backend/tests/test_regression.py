import pytest
import logging
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from models import Player, Game, Board
from schemas import PlayerLevel

# Create a test client
client = TestClient(app)
logger = logging.getLogger(__name__)

@pytest.mark.e2e
class TestEndToEndRegression:
    """End-to-end regression test for the full backend API flow.
    
    This test will verify the entire game flow from user registration to game completion.
    """
    
    def test_full_game_flow(self, test_db):
        """
        Complete end-to-end test of the application.
        
        Test plan:
        
        TODO #1: User creation and authentication
        - Create two users with different skill levels
        - Verify user profiles and initial ELO ratings
        - Test login/logout functionality
        - Verify site stats endpoint
        
        TODO #2: Game creation
        - Create a game directly in the database (simpler than using matchmaking)
        - Verify initial game state
        
        TODO #3: Play initial moves
        - Make several valid moves, alternating between players
        - Verify the game state is updated correctly
        - Specifically check the next_board constraint is followed
        - Log the full game state after each move
        
        TODO #4: Win a sub-board
        - Make moves to have player X win a specific sub-board
        - Verify the sub-board win is reflected in the meta-board state
        - Continue playing valid moves
        
        TODO #5: Complete the game
        - Have player X win enough sub-boards to win the entire game
        - Verify the game_over and winner fields are set correctly
        
        TODO #6: Verify ELO updates
        - Check that player profiles are updated with the correct wins/losses
        - Verify the ELO scores have been adjusted appropriately
        - Test profile update functionality
        """
        
        # TODO #1 implementation: User creation and authentication
        logger.info("Starting TODO #1: User creation and authentication")
        
        # Create two players with different skill levels
        player1_data = {
            "username": "player1",
            "email": "player1@example.com",
            "level": PlayerLevel.INTERMEDIATE,
            "timezone": "America/Los_Angeles",
            "country": "US"
        }
        
        player2_data = {
            "username": "player2",
            "email": "player2@example.com",
            "level": PlayerLevel.BEGINNER,
            "timezone": "America/New_York",
            "country": "US"
        }
        
        # Create player 1
        response = client.post("/auth/signup", json=player1_data)
        assert response.status_code == 200
        player1_id = response.json()["id"]
        logger.info(f"Created player1 with ID: {player1_id}")
        
        # Create player 2
        response = client.post("/auth/signup", json=player2_data)
        assert response.status_code == 200
        player2_id = response.json()["id"]
        logger.info(f"Created player2 with ID: {player2_id}")
        
        # Verify player profiles and initial ELO
        response = client.get(f"/profile/{player1_id}")
        assert response.status_code == 200
        player1_profile = response.json()
        assert player1_profile["username"] == "player1"
        assert player1_profile["stats"]["elo"] == 700  # INTERMEDIATE level
        
        response = client.get(f"/profile/{player2_id}")
        assert response.status_code == 200
        player2_profile = response.json()
        assert player2_profile["username"] == "player2"
        assert player2_profile["stats"]["elo"] == 400  # BEGINNER level
        
        # Test login functionality
        response = client.post("/auth/login", json={"email": "player1@example.com"})
        assert response.status_code == 200
        
        # Test logout functionality
        response = client.post("/auth/logout")
        assert response.status_code == 200
        
        # Verify site stats
        response = client.get("/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "games_today" in stats
        assert "players_online" in stats
        
        logger.info("Successfully completed TODO #1")
        
        # TODO #2 implementation: Game creation
        logger.info("Starting TODO #2: Game creation")
        
        # Create a game directly in the database
        game = Game.create(
            player_x=Player.get(Player.id == player1_id),
            player_o=Player.get(Player.id == player2_id),
            current_player="X",
            last_move_time=datetime.now(),
            started=True
        )
        game_id = game.id
        logger.info(f"Created game with ID: {game_id}")
        
        # Verify initial game state
        response = client.get(f"/games/{game_id}")
        assert response.status_code == 200
        game_state = response.json()
        
        # Check initial game state properties
        assert game_state["id"] == game_id
        assert game_state["current_player"] == "X"
        assert game_state["next_board"] is None  # No next_board constraint at the start
        assert game_state["winner"] is None
        assert game_state["game_over"] == False
        assert game_state["player_x"]["id"] == player1_id
        assert game_state["player_o"]["id"] == player2_id
        assert len(game_state["boards"]) == 9  # 9 sub-boards
        assert len(game_state["meta_board"]) == 9  # meta-board tracking sub-board wins
        
        # Check that all boards are empty at the start
        for board in game_state["boards"]:
            assert all(cell == "" for cell in board)
        
        # Check that meta-board is empty at the start
        assert all(cell == "" for cell in game_state["meta_board"])
        
        logger.info("Successfully completed TODO #2")

    def test_game_resignation(self, test_db):
        """Test that a player can resign from a game."""
        # Create two players
        player1 = Player.create(
            username="resign_player1",
            email="resign1@example.com",
            elo=1000
        )
        
        player2 = Player.create(
            username="resign_player2",
            email="resign2@example.com",
            elo=1000
        )
        
        # Create a game
        game = Game.create(
            player_x=player1,
            player_o=player2,
            current_player="X",
            started=True,
            last_move_time=datetime.now()
        )
        
        # Player O resigns
        response = client.post(f"/games/{game.id}/resign?player_id={player2.id}")
        assert response.status_code == 200
        game_state = response.json()
        
        # Verify game state
        assert game_state["game_over"] == True
        assert game_state["winner"] == "X"
        assert game_state["player_x"]["elo_change"] is not None
        assert game_state["player_o"]["elo_change"] is not None
        
        # Check that player stats were updated
        player1 = Player.get(Player.id == player1.id)
        player2 = Player.get(Player.id == player2.id)
        
        assert player1.wins == 1
        assert player2.losses == 1