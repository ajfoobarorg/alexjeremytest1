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
        
        Test plan divided into manageable steps with each step in its own method:
        
        TODO #1: User creation and authentication
        TODO #2: Game creation
        TODO #3: Play initial moves
        TODO #4: Win a sub-board
        TODO #5: Complete the game
        TODO #6: Verify ELO updates
        """
        # TODO #1: User creation and authentication
        player1_id, player2_id = self._create_users_and_verify()
        
        # TODO #2: Game creation
        game_id = self._create_game_and_verify(player1_id, player2_id)
        
        # TODO #3: Play initial moves
        # Commented out for now - will test after verifying first two parts work
        # self._play_initial_moves(game_id, player1_id, player2_id)
        
        # Remaining TODOs will be implemented later
        
    def _create_users_and_verify(self):
        """
        TODO #1: Create users and verify their profiles.
        
        - Create two users with different skill levels
        - Verify user profiles and initial ELO ratings
        - Test login/logout functionality
        - Verify site stats endpoint
        
        Returns:
            tuple: (player1_id, player2_id) - The IDs of the created players
        """
        logger.info("Starting TODO #1: User creation and authentication")
        
        # Create two players with different skill levels
        player1_data = {
            "username": "player1",
            "email": "player1@example.com",
            "level": PlayerLevel.INTERMEDIATE,  # This gives an ELO of 700
            "timezone": "America/Los_Angeles",
            "country": "US"
        }
        
        player2_data = {
            "username": "player2",
            "email": "player2@example.com",
            "level": PlayerLevel.BEGINNER,  # This gives an ELO of 400
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
        return player1_id, player2_id
        
    def _create_game_and_verify(self, player1_id, player2_id):
        """
        TODO #2: Create a game and verify its initial state.
        
        - Create a game directly in the database
        - Verify initial game state
        
        Args:
            player1_id: ID of player X
            player2_id: ID of player O
            
        Returns:
            str: The ID of the created game
        """
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
        return game_id
        
    def _play_initial_moves(self, game_id, player1_id, player2_id):
        """
        TODO #3: Play initial moves and verify game state after each move.
        
        - Make several valid moves, alternating between players
        - Verify the game state is updated correctly
        - Specifically check the next_board constraint is followed
        
        Args:
            game_id: ID of the game
            player1_id: ID of player X
            player2_id: ID of player O
            
        Returns:
            dict: The game state after the moves
        """
        logger.info("Starting TODO #3: Play initial moves")
        
        # Move 1: X plays in the center of the center board (board 4, position 4)
        logger.info("Move 1: X plays in center of center board (4, 4)")
        response = client.post(f"/games/{game_id}/move/4/4?player_id={player1_id}")
        assert response.status_code == 200
        game_state = response.json()
        
        # Verify move 1 results
        assert game_state["current_player"] == "O"  # Turn changed to O
        assert game_state["next_board"] == 4  # Next player must play in board 4
        assert game_state["boards"][4][4] == "X"  # X is placed in center of board 4
        
        # Log entire game state for debugging
        logger.info(f"Game state after move 1: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
        
        # Move 2: O plays in center board, top-left (board 4, position 0)
        logger.info("Move 2: O plays in center board, top-left (4, 0)")
        response = client.post(f"/games/{game_id}/move/4/0?player_id={player2_id}")
        assert response.status_code == 200
        game_state = response.json()
        
        # Verify move 2 results
        assert game_state["current_player"] == "X"  # Turn changed to X
        assert game_state["next_board"] == 0  # Next player must play in board 0
        assert game_state["boards"][4][0] == "O"  # O is placed in top-left of board 4
        
        logger.info(f"Game state after move 2: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
        
        # Move 3: X plays in top-left board, center (board 0, position 4)
        logger.info("Move 3: X plays in top-left board, center (0, 4)")
        response = client.post(f"/games/{game_id}/move/0/4?player_id={player1_id}")
        assert response.status_code == 200
        game_state = response.json()
        
        # Verify move 3 results
        assert game_state["current_player"] == "O"  # Turn changed to O
        assert game_state["next_board"] == 4  # Next player must play in board 4
        assert game_state["boards"][0][4] == "X"  # X is placed in center of board 0
        
        logger.info(f"Game state after move 3: boards[0] = {game_state['boards'][0]}, next_board = {game_state['next_board']}")
        
        # Move 4: O plays in center board, top-right (board 4, position 2)
        logger.info("Move 4: O plays in center board, top-right (4, 2)")
        response = client.post(f"/games/{game_id}/move/4/2?player_id={player2_id}")
        assert response.status_code == 200
        game_state = response.json()
        
        # Verify move 4 results
        assert game_state["current_player"] == "X"  # Turn changed to X
        assert game_state["next_board"] == 2  # Next player must play in board 2
        assert game_state["boards"][4][2] == "O"  # O is placed in top-right of board 4
        
        logger.info(f"Game state after move 4: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
        
        # Verify that no one has won any boards yet
        for board_index in range(9):
            assert game_state["meta_board"][board_index] == ""
        
        logger.info("Successfully completed TODO #3")
        return game_state

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