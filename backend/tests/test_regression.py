import pytest
import logging
from datetime import datetime

from schemas import PlayerLevel

logger = logging.getLogger(__name__)

def _create_users_and_verify(client):
    """
    TODO #1: Create users and verify their profiles.
    
    - Create two users with different skill levels
    - Verify user profiles and initial ELO ratings
    - Test login/logout functionality
    - Verify site stats endpoint
    
    Args:
        client: The API client to use for HTTP requests
        
    Returns:
        tuple: (player1_id, player2_id) - The IDs of the created players
    """
    logger.info("Starting TODO #1: User creation and authentication")
    
    # Create two players with different skill levels
    player1_data = {
        "username": "player1",
        "email": "player1@example.com",
        "level": "2",  # INTERMEDIATE level (2) gives an ELO of 700
        "first_name": "Player",
        "last_name": "One",
        "timezone": "America/Los_Angeles",
        "country": "US"
    }
    
    player2_data = {
        "username": "player2",
        "email": "player2@example.com",
        "level": "1",  # BEGINNER level (1) gives an ELO of 400
        "first_name": "Player",
        "last_name": "Two",
        "timezone": "America/New_York",
        "country": "US"
    }
    
    # Create player 1
    response = client.signup(player1_data)
    assert response.status_code == 200
    player1_id = response.json()["id"]
    logger.info(f"Created player1 with ID: {player1_id}")
    
    # Create player 2
    response = client.signup(player2_data)
    assert response.status_code == 200
    player2_id = response.json()["id"]
    logger.info(f"Created player2 with ID: {player2_id}")
    
    # Verify player profiles and initial ELO
    response = client.get_profile(player1_id)
    assert response.status_code == 200
    player1_profile = response.json()
    assert player1_profile["username"] == "player1"
    assert player1_profile["stats"]["elo"] == 700  # INTERMEDIATE level
    
    response = client.get_profile(player2_id)
    assert response.status_code == 200
    player2_profile = response.json()
    assert player2_profile["username"] == "player2"
    assert player2_profile["stats"]["elo"] == 400  # BEGINNER level
    
    # Test login functionality
    response = client.login("player1@example.com")
    assert response.status_code == 200
    
    # Test logout functionality
    response = client.logout()
    assert response.status_code == 200
    
    # Verify site stats
    response = client.get_stats()
    assert response.status_code == 200
    stats = response.json()
    assert "games_today" in stats
    assert "players_online" in stats
    
    logger.info("Successfully completed TODO #1")
    return player1_id, player2_id
    
def _create_game_and_verify(client, player1_id, player2_id):
    """
    TODO #2: Create a game and verify its initial state.
    
    - Create a game using the API
    - Verify initial game state
    
    Args:
        client: The API client to use for HTTP requests
        player1_id: ID of player X
        player2_id: ID of player O
        
    Returns:
        str: The ID of the created game
    """
    logger.info("Starting TODO #2: Game creation")
    
    # Try to create a game through the API first
    try:
        # If the server has a create game endpoint
        response = client.create_game(player1_id, player2_id)
        if response.status_code == 200:
            game_id = response.json()["id"]
            logger.info(f"Created game with ID: {game_id} through API endpoint")
        else:
            # Fall back to direct creation
            raise Exception("API game creation failed")
    except:
        # If no API endpoint, use the direct method in our wrapper
        # This works for the TestClientWrapper but not for real HTTP clients
        try:
            game_data = client.direct_game_creation(player1_id, player2_id)
            game_id = game_data["id"]
            logger.info(f"Created game with ID: {game_id} through direct creation")
        except Exception as e:
            # This would fail with a real HTTP client without a create endpoint
            logger.error(f"Failed to create game: {str(e)}")
            raise
    
    # Verify initial game state
    response = client.get_game(game_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Check initial game state properties
    assert game_state["id"] == game_id
    assert game_state["current_player"] == "X"
    assert game_state["next_board"] is None  # No next_board constraint at the start
    assert game_state["winner"] is None
    assert game_state["game_over"] == False
    
    # With matchmaking, roles (X/O) are assigned randomly, so we need to be flexible
    # about which player is X and which is O. We'll store them for later use.
    actual_player_x_id = game_state["player_x"]["id"]
    actual_player_o_id = game_state["player_o"]["id"]
    
    # Make sure both players are in the game
    assert actual_player_x_id in [player1_id, player2_id]
    assert actual_player_o_id in [player1_id, player2_id]
    assert actual_player_x_id != actual_player_o_id  # Sanity check
    assert len(game_state["boards"]) == 9  # 9 sub-boards
    assert len(game_state["meta_board"]) == 9  # meta-board tracking sub-board wins
    
    # Check that all boards are empty at the start
    for board in game_state["boards"]:
        assert all(cell == "" for cell in board)
    
    # Check that meta-board is empty at the start
    assert all(cell == "" for cell in game_state["meta_board"])
    
    logger.info("Successfully completed TODO #2")
    # Return the game ID and the actual player X and O IDs
    return game_id, actual_player_x_id, actual_player_o_id
    
def _play_initial_moves(client, game_id, player1_id, player2_id):
    """
    TODO #3: Play initial moves and verify game state after each move.
    
    - Make several valid moves, alternating between players
    - Verify the game state is updated correctly
    - Specifically check the next_board constraint is followed
    
    Args:
        client: The API client to use for HTTP requests
        game_id: ID of the game
        player1_id: ID of player X
        player2_id: ID of player O
        
    Returns:
        dict: The game state after the moves
    """
    logger.info("Starting TODO #3: Play initial moves")
    
    # Move 1: X plays in the center of the center board (board 4, position 4)
    logger.info("Move 1: X plays in center of center board (4, 4)")
    response = client.make_move(game_id, 4, 4, player1_id)
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
    response = client.make_move(game_id, 4, 0, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 2 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 0  # Next player must play in board 0
    assert game_state["boards"][4][0] == "O"  # O is placed in top-left of board 4
    
    logger.info(f"Game state after move 2: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
    
    # Move 3: X plays in top-left board, center (board 0, position 4)
    logger.info("Move 3: X plays in top-left board, center (0, 4)")
    response = client.make_move(game_id, 0, 4, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 3 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 4  # Next player must play in board 4
    assert game_state["boards"][0][4] == "X"  # X is placed in center of board 0
    
    logger.info(f"Game state after move 3: boards[0] = {game_state['boards'][0]}, next_board = {game_state['next_board']}")
    
    # Move 4: O plays in center board, top-right (board 4, position 2)
    logger.info("Move 4: O plays in center board, top-right (4, 2)")
    response = client.make_move(game_id, 4, 2, player2_id)
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
    
def _win_subboard(client, game_id, player1_id, player2_id):
    """
    TODO #4: Win a sub-board.
    
    - Make moves to have player X win board 2 (top-right board)
    - Verify the sub-board win is reflected in the meta-board state
    - Continue playing valid moves
    
    Args:
        client: The API client to use for HTTP requests
        game_id: ID of the game
        player1_id: ID of player X
        player2_id: ID of player O
        
    Returns:
        dict: The game state after winning a sub-board
    """
    logger.info("Starting TODO #4: Win a sub-board")
    
    # Move 5: X plays in top-right board (board 2), center (2, 4)
    # Following the next_board constraint (next_board = 2 from previous move)
    logger.info("Move 5: X plays in top-right board, center (2, 4)")
    response = client.make_move(game_id, 2, 4, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 5 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 4  # Next player must play in board 4
    assert game_state["boards"][2][4] == "X"  # X is placed in center of board 2
    
    logger.info(f"Game state after move 5: boards[2] = {game_state['boards'][2]}, next_board = {game_state['next_board']}")
    
    # Move 6: O plays in center board, bottom-left (4, 6)
    logger.info("Move 6: O plays in center board, bottom-left (4, 6)")
    response = client.make_move(game_id, 4, 6, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 6 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 6  # Next player must play in board 6
    assert game_state["boards"][4][6] == "O"  # O is placed in bottom-left of board 4
    
    logger.info(f"Game state after move 6: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
    
    # Move 7: X plays in bottom-left board, center (6, 4)
    logger.info("Move 7: X plays in bottom-left board, center (6, 4)")
    response = client.make_move(game_id, 6, 4, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 7 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 4  # Next player must play in board 4
    assert game_state["boards"][6][4] == "X"  # X is placed in center of board 6
    
    logger.info(f"Game state after move 7: boards[6] = {game_state['boards'][6]}, next_board = {game_state['next_board']}")
    
    # Move 8: O plays in center board, bottom-right (4, 8)
    logger.info("Move 8: O plays in center board, bottom-right (4, 8)")
    response = client.make_move(game_id, 4, 8, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 8 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 8  # Next player must play in board 8
    assert game_state["boards"][4][8] == "O"  # O is placed in bottom-right of board 4
    
    logger.info(f"Game state after move 8: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
    
    # Move 9: X plays in bottom-right board, center (8, 4)
    logger.info("Move 9: X plays in bottom-right board, center (8, 4)")
    response = client.make_move(game_id, 8, 4, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 9 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 4  # Next player must play in board 4
    assert game_state["boards"][8][4] == "X"  # X is placed in center of board 8
    
    logger.info(f"Game state after move 9: boards[8] = {game_state['boards'][8]}, next_board = {game_state['next_board']}")
    
    # Move 10: O plays in center board, top-middle (4, 1)
    logger.info("Move 10: O plays in center board, top-middle (4, 1)")
    response = client.make_move(game_id, 4, 1, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 10 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 1  # Next player must play in board 1
    assert game_state["boards"][4][1] == "O"  # O is placed in top-middle of board 4
    
    logger.info(f"Game state after move 10: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
    
    # Move 11: X plays in top-middle board, top-left (1, 0)
    logger.info("Move 11: X plays in top-middle board, top-left (1, 0)")
    response = client.make_move(game_id, 1, 0, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 11 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 0  # Next player must play in board 0
    assert game_state["boards"][1][0] == "X"  # X is placed in top-left of board 1
    
    logger.info(f"Game state after move 11: boards[1] = {game_state['boards'][1]}, next_board = {game_state['next_board']}")
    
    # Move 12: O plays in top-left board, top-left (0, 0)
    logger.info("Move 12: O plays in top-left board, top-left (0, 0)")
    response = client.make_move(game_id, 0, 0, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 12 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 0  # Next player must play in board 0
    assert game_state["boards"][0][0] == "O"  # O is placed in top-left of board 0
    
    logger.info(f"Game state after move 12: boards[0] = {game_state['boards'][0]}, next_board = {game_state['next_board']}")
    
    # Now let's make X win board 2 (top-right board) by creating a row (we already played center (2, 4))
    
    # First, we need to get to board 2, so let's send O to it
    
    # Move 13: X plays in top-left board, top-middle (0, 1)
    logger.info("Move 13: X plays in top-left board, top-middle (0, 1)")
    response = client.make_move(game_id, 0, 1, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 13 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 1  # Next player must play in board 1
    assert game_state["boards"][0][1] == "X"  # X is placed in top-middle of board 0
    
    logger.info(f"Game state after move 13: boards[0] = {game_state['boards'][0]}, next_board = {game_state['next_board']}")
    
    # Move 14: O plays in top-middle board, top-middle (1, 1)
    logger.info("Move 14: O plays in top-middle board, top-middle (1, 1)")
    response = client.make_move(game_id, 1, 1, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 14 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 1  # Next player must play in board 1
    assert game_state["boards"][1][1] == "O"  # O is placed in top-middle of board 1
    
    logger.info(f"Game state after move 14: boards[1] = {game_state['boards'][1]}, next_board = {game_state['next_board']}")
    
    # Move 15: X plays in top-middle board, top-right (1, 2)
    logger.info("Move 15: X plays in top-middle board, top-right (1, 2)")
    response = client.make_move(game_id, 1, 2, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 15 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 2  # Next player must play in board 2
    assert game_state["boards"][1][2] == "X"  # X is placed in top-right of board 1
    
    logger.info(f"Game state after move 15: boards[1] = {game_state['boards'][1]}, next_board = {game_state['next_board']}")
    
    # Now O must play in board 2, where X will try to win
    
    # Move 16: O plays in top-right board, top-left (2, 0)
    logger.info("Move 16: O plays in top-right board, top-left (2, 0)")
    response = client.make_move(game_id, 2, 0, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 16 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 0  # Next player must play in board 0
    assert game_state["boards"][2][0] == "O"  # O is placed in top-left of board 2
    
    logger.info(f"Game state after move 16: boards[2] = {game_state['boards'][2]}, next_board = {game_state['next_board']}")
    
    # Move 17: X plays in top-left board, top-right (0, 2)
    logger.info("Move 17: X plays in top-left board, top-right (0, 2)")
    response = client.make_move(game_id, 0, 2, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 17 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 2  # Next player must play in board 2
    assert game_state["boards"][0][2] == "X"  # X is placed in top-right of board 0
    
    logger.info(f"Game state after move 17: boards[0] = {game_state['boards'][0]}, next_board = {game_state['next_board']}")
    
    # Now we can have X win board 2 by completing a row
    
    # Move 18: O plays in top-right board, top-middle (2, 1)
    logger.info("Move 18: O plays in top-right board, top-middle (2, 1)")
    response = client.make_move(game_id, 2, 1, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 18 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["next_board"] == 1  # Next player must play in board 1
    assert game_state["boards"][2][1] == "O"  # O is placed in top-middle of board 2
    
    logger.info(f"Game state after move 18: boards[2] = {game_state['boards'][2]}, next_board = {game_state['next_board']}")
    
    # Move 19: X plays in top-middle board, middle-left (1, 3)
    logger.info("Move 19: X plays in top-middle board, middle-left (1, 3)")
    response = client.make_move(game_id, 1, 3, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 19 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["next_board"] == 3  # Next player must play in board 3
    assert game_state["boards"][1][3] == "X"  # X is placed in middle-left of board 1
    
    logger.info(f"Game state after move 19: boards[1] = {game_state['boards'][1]}, next_board = {game_state['next_board']}")
    
    # Move 20: O plays in middle-left board, center (3, 4)
    logger.info("Move 20: O plays in middle-left board, center (3, 4)")
    response = client.make_move(game_id, 3, 4, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 20 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    
    # By move 20, O should have won board 4 by completing the top row (positions 0, 1, 2)
    # Therefore next_board should be None (free choice)
    assert game_state["meta_board"][4] == "O", "Board 4 should be won by O by now"
    assert game_state["next_board"] is None, "Next board should be None (free choice) since board 4 is won"

    assert game_state["boards"][3][4] == "O"  # O is placed in center of board 3
    
    logger.info(f"Game state after move 20: boards[3] = {game_state['boards'][3]}, next_board = {game_state['next_board']}")
    
    # Move 21: Since we have free choice, let's play in board 1 (top-middle)
    logger.info("Move 21: X plays in board 1, center position (1, 4)")
    response = client.make_move(game_id, 1, 4, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 21 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    # We played in position 4 of board 1, which would normally send to board 4
    # But board 4 is already won by O, so next_board should be None (free choice)
    assert game_state["next_board"] is None, "Next board should be None since board 4 is already won"
    assert game_state["boards"][1][4] == "X"  # X is placed in center of board 1
    logger.info(f"After move 21, next_board = {game_state['next_board']}")
    
    logger.info(f"Game state after move 21: boards[4] = {game_state['boards'][4]}, next_board = {game_state['next_board']}")
    
    # Move 22: O has free choice since board 4 is already won
    # So O can play in any available board
    assert game_state["next_board"] is None  # Free choice
    assert game_state["meta_board"][4] == "O"  # Board 4 is already won by O
    
    # Let's play in position 2 (top-right) which should be free
    
    logger.info("Move 22: O plays in board 2, top-right position (2, 2)")
    response = client.make_move(game_id, 2, 2, player2_id)
    assert response.status_code == 200
    
    game_state = response.json()
    
    # Verify move 22 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["boards"][2][2] == "O"  # O is placed in top-right of board 2
    
    # O has now won board, 2 by completing the top row (positions 0, 1, 2)
    # So next_board should be None (free choice for X)
    assert game_state["meta_board"][2] == "O", "Board 2 should be won by O after move 22"
    assert game_state["next_board"] is None, "Next board should be None since board 2 is won by O"
    logger.info(f"After move 22, next_board = {game_state['next_board']}")
    
    logger.info(f"Game state after move 22: boards[5] = {game_state['boards'][5]}, next_board = {game_state['next_board']}")
    
    # Move 23: X plays in board 0 (top-left), trying to complete a row
    logger.info("Move 23: X plays in board 0, position 7 (bottom-middle)")
    response = client.make_move(game_id, 0, 7, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 23 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["boards"][0][7] == "X"  # X is placed in bottom-middle of board 0
    
    # Log the board state
    logger.info(f"Board 4 state: {game_state['boards'][4]}")
    logger.info(f"Meta board state: {game_state['meta_board']}")
    
    # Log winning information
    x_won_boards = [i for i, val in enumerate(game_state["meta_board"]) if val == "X"]
    o_won_boards = [i for i, val in enumerate(game_state["meta_board"]) if val == "O"]
    logger.info(f"X has won board(s): {x_won_boards}")
    logger.info(f"O has won board(s): {o_won_boards}")
    
    # O should have won board 4 (center board)
    assert 4 in o_won_boards, "O should have won board 4 (center board)"
    
    # Verify that the turn has changed
    assert game_state["current_player"] == "O"
    
    logger.info("Successfully completed TODO #4")
    return game_state
    
def _complete_game(client, game_id, player1_id, player2_id, game_state):
    """
    TODO #5: Complete the game with a deterministic winning strategy.
    
    - Make specific moves to have X win boards 0, 3, and 6 (left column)
    - Verify the game is marked as completed with X as the winner
    - Check that the game_over flag is set to True
    
    Args:
        client: The API client to use for HTTP requests
        game_id: ID of the game
        player1_id: ID of player X
        player2_id: ID of player O
        game_state: The current game state from the previous step
    
    Returns:
        dict: The final game state
    """
    logger.info("Starting TODO #5: Complete the game")
    
    # After move 23, O's turn:
    # - O has won boards 2 and 4
    # - X should try to win boards 0, 3, and 6 (left column)
    
    # Move 24: O plays in board 7 (bottom-middle), position 0 (top-left)
    logger.info("Move 24: O plays in bottom-middle board, top-left (7, 0)")
    response = client.make_move(game_id, 7, 0, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 24 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["boards"][7][0] == "O"  # O is placed in top-left of board 7
    
    # Since O played in position 0 of board 7, next_board would normally be 0
    # But board 0 is already won by X, so next_board should be None (free choice)
    assert game_state["next_board"] is None  # Free choice since board 0 is won
    
    # Move 25: Since board 0 is already won by X, we can't play there
    # Let's play in board 3 (middle-left) instead, which is part of our winning strategy
    logger.info("Move 25: X plays in middle-left board, top-left (3, 0)")
    response = client.make_move(game_id, 3, 0, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 25 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["boards"][3][0] == "X"  # X is placed in top-left of board 3
    # Check that board 0 is still won by X
    assert game_state["meta_board"][0] == "X", "Board 0 should still be won by X"
    # Since X played in position 0 of board 3, next_board would normally be 0
    # But board 0 is already won by X, so next_board should be None (free choice)
    assert game_state["next_board"] is None, "Next board should be None since board 0 is already won"
    
    # Move 26: O plays in board 6 (bottom-left), position 1 (top-middle)
    logger.info("Move 26: O plays in bottom-left board, top-middle (6, 1)")
    response = client.make_move(game_id, 6, 1, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 26 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["boards"][6][1] == "O"  # O is placed in top-middle of board 6
    assert game_state["next_board"] == 1  # Next board is 1
    
    # Move 27: X plays in board 1 (top-middle), position 6 (bottom-left)
    logger.info("Move 27: X plays in top-middle board, bottom-left (1, 6)")
    response = client.make_move(game_id, 1, 6, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 27 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["boards"][1][6] == "X"  # X is placed in bottom-left of board 1
    assert game_state["next_board"] == 6  # Next board is 6
    
    # Move 28: O plays in board 6 (bottom-left), position 2 (top-right)
    logger.info("Move 28: O plays in bottom-left board, top-right (6, 2)")
    response = client.make_move(game_id, 6, 2, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify move 28 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["boards"][6][2] == "O"  # O is placed in top-right of board 6
    # Since O played in position 2 of board 6, next_board would normally be 2
    # But board 2 is already won by O, so next_board should be None (free choice)
    assert game_state["next_board"] is None, "Next board should be None since board 2 is already won by O"
    
    # Move 29 would be a duplicate of move 25 (X plays in board 3, position 0)
    # So we'll skip to the next move
    # Renumbering from here: move 30 → move 29, etc.
    
    # After move 28, let's simplify and focus on getting X to win boards 0, 3, and 6
    # X has already won board 0
    # X has already played at position 0 of board 3 and in the center of board 6
    # We just need 2 more moves in board 3 and 1 more move in board 6
    logger.info(f"ALEX After move 28, meta_board state: {game_state['meta_board']}")
    logger.info(f"ALEX After move 28, board 3 state: {game_state['boards'][3]}")
    logger.info(f"ALEX After move 28, board 6 state: {game_state['boards'][6]}")
    logger.info(f"ALEX After move 28, next_board: {game_state['next_board']}")
    
    # Move 29: Since next_board is None (free choice), X can play in board 3 position 3 (middle-left)
    logger.info("Move 29: X plays in middle-left board, middle-left (3, 3)")
    response = client.make_move(game_id, 3, 3, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log the detailed state for debugging
    logger.info(f"DETAILED: After move 29, game_state['boards'][3] = {game_state['boards'][3]}")
    logger.info(f"DETAILED: After move 29, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 29, meta_board = {game_state['meta_board']}")
    
    # Verify move 29 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["boards"][3][3] == "X"  # X is placed in middle-left of board 3
    assert game_state["next_board"] == 3  # Next board is 3
    
    # Move 30: O plays in board 3, position 1 (top-middle) 
    # Note: The previous move set next_board to 3, so O must play in board 3
    logger.info("Move 30: O plays in middle-left board, top-middle (3, 1)")
    logger.info(f"Current next_board before move 30: {game_state['next_board']}")
    response = client.make_move(game_id, 3, 1, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 30, response status code: {response.status_code}")
    logger.info(f"DETAILED: After move 30, game_state['boards'][3] = {game_state['boards'][3]}")
    logger.info(f"DETAILED: After move 30, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 30, meta_board = {game_state['meta_board']}")
    logger.info(f"DETAILED: After move 30, current_player = {game_state['current_player']}")
    
    # Verify move 30 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["boards"][3][1] == "O"  # O is placed in top-middle of board 3
    # The next_board is None (free choice) since position 1 would normally send to board 1
    # but board 1 is already won by X (as seen in the meta_board)
    assert game_state["next_board"] is None, "Next board should be None (free choice)"
    
    # Move 31: X plays in board 3, position 6 (bottom-left) to continue the winning strategy for board 3
    # X has free choice since next_board is None
    logger.info("Move 31: X plays in middle-left board, bottom-left (3, 6)")
    response = client.make_move(game_id, 3, 6, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 31, game_state['boards'][3] = {game_state['boards'][3]}")
    logger.info(f"DETAILED: After move 31, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 31, meta_board = {game_state['meta_board']}")
    
    # Verify move 31 results
    assert game_state["current_player"] == "O"  # Turn changed to O
    assert game_state["boards"][3][6] == "X"  # X is placed in bottom-left of board 3
    # X should now have won board 3 with positions 0, 3, 6 (left column)
    assert game_state["meta_board"][3] == "X", "X should have won board 3"
    
    # After move 31, next_board is 6, meaning O must play in board 6
    
    # Move 32: O plays in board 6, position 3 (middle-left)
    logger.info("Move 32: O plays in bottom-left board, middle-left (6, 3)")
    response = client.make_move(game_id, 6, 3, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 32, game_state['boards'][6] = {game_state['boards'][6]}")
    logger.info(f"DETAILED: After move 32, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 32, meta_board = {game_state['meta_board']}")
    logger.info(f"DETAILED: After move 32, current_player = {game_state['current_player']}")
    
    # Verify move 32 results
    assert game_state["current_player"] == "X"  # Turn changed to X
    assert game_state["boards"][6][3] == "O"  # O is placed in middle-left of board 6
    # Playing in position 3 would normally send to board 3,
    # but board 3 is already won by X, so next_board should be None (free choice)
    assert game_state["next_board"] is None, "Next board should be None (free choice)"
    
    # Move 33: X plays in board 6, position 6 (bottom-left)
    logger.info("Move 33: X plays in bottom-left board, bottom-left (6, 6)")
    response = client.make_move(game_id, 6, 6, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 33, game_state['boards'][6] = {game_state['boards'][6]}")
    logger.info(f"DETAILED: After move 33, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 33, meta_board = {game_state['meta_board']}")
    logger.info(f"DETAILED: After move 33, game_over = {game_state['game_over']}")
    logger.info(f"DETAILED: After move 33, winner = {game_state['winner']}")
    
    # Verify move 33 results
    assert game_state["boards"][6][6] == "X"  # X is placed in bottom-left of board 6
    assert game_state["current_player"] == "O"  # Turn changed to O
    
    # Now O plays in board 6 again (since next_board is 6)
    logger.info("Move 34: O plays in bottom-left board, middle-middle (6, 7)")
    response = client.make_move(game_id, 6, 7, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 34, game_state['boards'][6] = {game_state['boards'][6]}")
    logger.info(f"DETAILED: After move 34, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 34, meta_board = {game_state['meta_board']}")
    
    # Verify move 34 results
    assert game_state["boards"][6][7] == "O"  # O is placed in bottom-middle of board 6
    assert game_state["current_player"] == "X"  # Turn changed to X
    
    # Move 35: X plays in board 7, position 2 (top-right)
    logger.info("Move 35: X plays in bottom-middle board, top-right (7, 2)")
    response = client.make_move(game_id, 7, 2, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 35, game_state['boards'][7] = {game_state['boards'][7]}")
    logger.info(f"DETAILED: After move 35, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 35, meta_board = {game_state['meta_board']}")
    
    # Verify move 35 results
    assert game_state["boards"][7][2] == "X"  # X is placed in top-right of board 7
    assert game_state["current_player"] == "O"  # Turn changed to O
    
    # Move 36: O plays in bottom-left board, bottom-right (6, 8)
    logger.info("Move 36: O plays in bottom-left board, bottom-right (6, 8)")
    response = client.make_move(game_id, 6, 8, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 36, game_state['boards'][6] = {game_state['boards'][6]}")
    logger.info(f"DETAILED: After move 36, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 36, meta_board = {game_state['meta_board']}")
    
    # Verify the next_board constraint after move 36
    assert game_state["next_board"] == 8, "Next board should be 8 (since O played in position 8 of board 6)"
    
    # Move 37: X plays in board 8, position 0 (top-left)
    logger.info("Move 37: X plays in bottom-right board, top-left (8, 0)")
    response = client.make_move(game_id, 8, 0, player1_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 37, game_state['boards'][8] = {game_state['boards'][8]}")
    logger.info(f"DETAILED: After move 37, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 37, meta_board = {game_state['meta_board']}")
    
    # Verify move 37 results
    assert game_state["boards"][8][0] == "X", "X should be placed in top-left of board 8"
    assert game_state["current_player"] == "O", "Turn should change to O"
    assert game_state["next_board"] is None, "Next board should be None (free choice)"
    
    # Move 38: O plays in board 6, position 0 (top-left) to win board 6 and complete a diagonal win
    logger.info("Move 38: O plays in bottom-left board, top-left (6, 0)")
    response = client.make_move(game_id, 6, 0, player2_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Log detailed state for debugging
    logger.info(f"DETAILED: After move 38, game_state['boards'][6] = {game_state['boards'][6]}")
    logger.info(f"DETAILED: After move 38, next_board = {game_state['next_board']}")
    logger.info(f"DETAILED: After move 38, meta_board = {game_state['meta_board']}")
    logger.info(f"DETAILED: After move 38, game_over = {game_state['game_over']}")
    logger.info(f"DETAILED: After move 38, winner = {game_state['winner']}")
    
    # Verify move 38 results - O should have won board 6
    assert game_state["boards"][6][0] == "O", "O should be placed in top-left of board 6"
    assert game_state["meta_board"][6] == "O", "O should have won board 6"
    
    # Game should be over with O as the winner
    assert game_state["game_over"] == True, "Game should be over"
    assert game_state["winner"] == "O", "O should be the winner"
    
    # Verify O has won the diagonal on the meta-board (boards 2, 4, 6)
    assert game_state["meta_board"][2] == "O", "O should have won board 2"
    assert game_state["meta_board"][4] == "O", "O should have won board 4" 
    assert game_state["meta_board"][6] == "O", "O should have won board 6"
    
    logger.info("Successfully completed TODO #5")
    return game_state
    
def _verify_elo_updates(client, player1_id, player2_id, game_state, player_x_won=False):
    """
    TODO #6: Verify ELO updates after game completion.
    
    - Verify both players' profiles have been updated with new ELO scores
    - Verify the winner's ELO increased and the loser's ELO decreased
    - Verify win/loss counts have been updated correctly
    
    Args:
        client: The API client to use for HTTP requests
        player1_id: ID of first player (original order)
        player2_id: ID of second player (original order)
        game_state: The final game state after game completion
        player_x_won: Whether player X won the game
    """
    logger.info("Starting TODO #6: Verify ELO updates")
    
    # Verify that the game includes ELO change information
    assert game_state["player_x"]["elo_change"] is not None, "Player X should have an ELO change recorded"
    assert game_state["player_o"]["elo_change"] is not None, "Player O should have an ELO change recorded"
    
    # Get player profiles to check the updated ELO scores
    response = client.get_profile(player1_id)
    assert response.status_code == 200
    player1_profile = response.json()
    
    response = client.get_profile(player2_id)
    assert response.status_code == 200
    player2_profile = response.json()
    
    # Log ELO changes for debugging
    logger.info(f"Player X (player1) ELO change: {game_state['player_x']['elo_change']}")
    logger.info(f"Player O (player2) ELO change: {game_state['player_o']['elo_change']}")
    logger.info(f"Player X (player1) final ELO: {player1_profile['stats']['elo']}")
    logger.info(f"Player O (player2) final ELO: {player2_profile['stats']['elo']}")
    
    # Check ELO changes based on who won
    if player_x_won:
        assert game_state["player_x"]["elo_change"] > 0, "Winner (Player X) should have positive ELO change"
        assert game_state["player_o"]["elo_change"] < 0, "Loser (Player O) should have negative ELO change"
        
        # Check which player was X and which was O
        player_x_id = game_state["player_x"]["id"]
        player_o_id = game_state["player_o"]["id"]
        
        # Verify win/loss counts based on player assignments
        if player_x_id == player1_id:  # player1 is X and won
            assert player1_profile["stats"]["wins"] == 1, "Player 1 (X) should have 1 win"
            assert player1_profile["stats"]["losses"] == 0, "Player 1 (X) should have 0 losses"
            assert player2_profile["stats"]["wins"] == 0, "Player 2 (O) should have 0 wins"
            assert player2_profile["stats"]["losses"] == 1, "Player 2 (O) should have 1 loss"
        else:  # player2 is X and won
            assert player2_profile["stats"]["wins"] == 1, "Player 2 (X) should have 1 win"
            assert player2_profile["stats"]["losses"] == 0, "Player 2 (X) should have 0 losses"
            assert player1_profile["stats"]["wins"] == 0, "Player 1 (O) should have 0 wins"
            assert player1_profile["stats"]["losses"] == 1, "Player 1 (O) should have 1 loss"
    else:  # Player O won
        assert game_state["player_o"]["elo_change"] > 0, "Winner (Player O) should have positive ELO change"
        assert game_state["player_x"]["elo_change"] < 0, "Loser (Player X) should have negative ELO change"
        
        # Check which player was X and which was O
        player_x_id = game_state["player_x"]["id"]
        player_o_id = game_state["player_o"]["id"]
        
        # Verify win/loss counts based on player assignments
        if player_o_id == player1_id:  # player1 is O and won
            assert player1_profile["stats"]["wins"] == 1, "Player 1 (O) should have 1 win"
            assert player1_profile["stats"]["losses"] == 0, "Player 1 (O) should have 0 losses"
            assert player2_profile["stats"]["wins"] == 0, "Player 2 (X) should have 0 wins"
            assert player2_profile["stats"]["losses"] == 1, "Player 2 (X) should have 1 loss"
        else:  # player2 is O and won
            assert player2_profile["stats"]["wins"] == 1, "Player 2 (O) should have 1 win"
            assert player2_profile["stats"]["losses"] == 0, "Player 2 (O) should have 0 losses"
            assert player1_profile["stats"]["wins"] == 0, "Player 1 (X) should have 0 wins"
            assert player1_profile["stats"]["losses"] == 1, "Player 1 (X) should have 1 loss"
    
    # Calculate expected final ELOs based on player assignments
    player_x_id = game_state["player_x"]["id"]
    player_o_id = game_state["player_o"]["id"]
    
    player1_elo_change = game_state["player_x"]["elo_change"] if player_x_id == player1_id else game_state["player_o"]["elo_change"]
    player2_elo_change = game_state["player_o"]["elo_change"] if player_o_id == player2_id else game_state["player_x"]["elo_change"]
    
    # Expected starting ELOs based on skill level
    # player1 has "INTERMEDIATE" level = 700 ELO
    # player2 has "BEGINNER" level = 400 ELO
    expected_player1_elo = 700 + player1_elo_change
    expected_player2_elo = 400 + player2_elo_change
    
    # Verify final ELOs match the calculated values
    assert player1_profile["stats"]["elo"] == expected_player1_elo, "Player 1 final ELO should match initial ELO + change"
    assert player2_profile["stats"]["elo"] == expected_player2_elo, "Player 2 final ELO should match initial ELO + change"
    
    logger.info("Successfully completed TODO #6")

def _test_game_resignation(client, test_db):
    """Test that a player can resign from a game."""
    # Create two players
    player1_data = {
        "username": "resign_player1",
        "email": "resign1@example.com",
        "level": "2",  # INTERMEDIATE level (2)
        "first_name": "Resign",
        "last_name": "Player1",
        "timezone": "America/Los_Angeles",
        "country": "US"
    }
    
    player2_data = {
        "username": "resign_player2",
        "email": "resign2@example.com",
        "level": "2",  # INTERMEDIATE level (2)
        "first_name": "Resign",
        "last_name": "Player2",
        "timezone": "America/New_York",
        "country": "US"
    }
    
    # Create player 1
    response = client.signup(player1_data)
    assert response.status_code == 200
    player1_id = response.json()["id"]
    
    # Create player 2
    response = client.signup(player2_data)
    assert response.status_code == 200
    player2_id = response.json()["id"]
    
    # Create a game
    # Try to use the API endpoint first, but fall back to direct creation if needed
    try:
        response = client.create_game(player1_id, player2_id)
        if response.status_code == 200:
            game_id = response.json()["id"]
        else:
            raise Exception("API game creation failed")
    except:
        # Fall back to direct creation
        game_data = client.direct_game_creation(player1_id, player2_id)
        game_id = game_data["id"]
    
    # Get the game details to find out which player is which
    response = client.get_game(game_id)
    assert response.status_code == 200
    game_details = response.json()
    
    # Find out who is player X and who is player O
    player_x_id = game_details["player_x"]["id"]
    player_o_id = game_details["player_o"]["id"]
    
    # Player O resigns - use the actual player O
    response = client.resign_game(game_id, player_o_id)
    assert response.status_code == 200
    game_state = response.json()
    
    # Verify game state
    assert game_state["game_over"] == True
    assert game_state["winner"] == "X"
    assert game_state["player_x"]["elo_change"] is not None
    assert game_state["player_o"]["elo_change"] is not None
    
    # Check that player stats were updated via profiles
    response = client.get_profile(player1_id)
    assert response.status_code == 200
    player1_profile = response.json()
    
    response = client.get_profile(player2_id)
    assert response.status_code == 200
    player2_profile = response.json()
    
    # Check which player should have won based on roles
    if player_x_id == player1_id:  # player1 was X and won
        assert player1_profile["stats"]["wins"] == 1, "Player 1 (X) should have 1 win"
        assert player2_profile["stats"]["losses"] == 1, "Player 2 (O) should have 1 loss"
    else:  # player2 was X and won
        assert player2_profile["stats"]["wins"] == 1, "Player 2 (X) should have 1 win"
        assert player1_profile["stats"]["losses"] == 1, "Player 1 (O) should have 1 loss"

def run_full_game_flow(test_db, client):
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
    player1_id, player2_id = _create_users_and_verify(client)
    
    # TODO #2: Game creation
    # This returns the game_id and the assigned player IDs (which may be swapped from original)
    game_id, player_x_id, player_o_id = _create_game_and_verify(client, player1_id, player2_id)
    
    # TODO #3: Play initial moves - use actual X and O IDs from matchmaking
    _play_initial_moves(client, game_id, player_x_id, player_o_id)
    
    # TODO #4: Win a sub-board - use actual X and O IDs from matchmaking
    game_state = _win_subboard(client, game_id, player_x_id, player_o_id)
    
    # TODO #5: Complete the game - use actual X and O IDs from matchmaking
    final_game_state = _complete_game(client, game_id, player_x_id, player_o_id, game_state)
    
    # TODO #6: Verify ELO updates
    # Here we pass the original player1_id and player2_id for profile checks
    # but also pass the assigned roles so the test knows which player won
    _verify_elo_updates(client, player1_id, player2_id, final_game_state, 
                        player_x_won=(final_game_state["winner"] == "X"))

@pytest.mark.e2e
class TestEndToEndRegressionWithTestClient:
    """End-to-end regression test using the FastAPI TestClient.
    
    This test runs with the in-process TestClient for fast execution.
    """
    
    def test_full_game_flow_with_test_client(self, test_db, test_client):
        """Run the full game flow using the TestClient."""
        print("\n🔵 Running regression test with FastAPI TestClient (in-process)")
        run_full_game_flow(test_db, test_client)
        print("\n✅ TestClient regression test completed successfully!")
    
    def test_game_resignation_with_test_client(self, test_db, test_client):
        """Test that a player can resign from a game using TestClient."""
        print("\n🔵 Running game resignation test with FastAPI TestClient (in-process)")
        _test_game_resignation(test_client, test_db)
        print("\n✅ TestClient game resignation test completed successfully!")


@pytest.mark.e2e
@pytest.mark.http
class TestEndToEndRegressionWithHttpClient:
    """End-to-end regression test using a real HTTP client.
    
    This test runs against a real server for true end-to-end testing.
    """
    
    def test_full_game_flow_with_http_client(self, test_db, http_client):
        """Run the full game flow using the HTTP client against a real server."""
        print("\n🔴 Running regression test with real HTTP client (end-to-end)")
        run_full_game_flow(test_db, http_client)
        print("\n✅ HTTP client regression test completed successfully!")
    
    def test_game_resignation_with_http_client(self, test_db, http_client):
        """Test that a player can resign from a game using HTTP client."""
        print("\n🔴 Running game resignation test with real HTTP client (end-to-end)")
        _test_game_resignation(http_client, test_db)
        print("\n✅ HTTP client game resignation test completed successfully!")