import pytest
import json
from datetime import datetime, timedelta
from freezegun import freeze_time
from services import GameService
from models import Game, Player

#TODO(aroetter): pytest genreates 104 warnings, lets fix.

@pytest.mark.game_logic
class TestGameLogic:
    @staticmethod
    def start_game(game):
        game.last_move_time = datetime.now()
        game.started = True
        game.save()

    def test_move_to_completed_board(self, sample_players):
        """Test that moves to already completed boards are rejected."""
        # Set up a completed board (board 0)
        boards = [[""]*9 for _ in range(9)]
        boards[0] = ["X", "X", "X", "O", "O", "", "", "", ""]  # X wins top row
        
        active_game = Game.create(
            player_x=sample_players[0],
            player_o=sample_players[1],
            current_player="X",
            boards=json.dumps(boards)
        )
        self.start_game(active_game)
        
        # Attempt move in completed board
        game, error = GameService.make_move(
            active_game.id,
            board_index=0,
            position=5,
            player_id=sample_players[0].id
        )
        
        assert error == "Board already completed"
        assert game is None

    def test_out_of_turn_move(self, sample_players):
        """Test that players cannot make moves out of turn."""
        active_game = Game.create(
            player_x=sample_players[0],
            player_o=sample_players[1],
            current_player="X",
            next_board=4
        )
        self.start_game(active_game)

        # Player O tries to move when it's X's turn
        game, error = GameService.make_move(
            active_game.id,
            board_index=4,
            position=4,
            player_id=sample_players[1].id  # Player O
        )
        
        assert error == "Not your turn"
        assert game is None

    def test_move_to_wrong_board(self, sample_players):
        """Test that moves must be made in the correct board when specified."""
        active_game = Game.create(
            player_x=sample_players[0],
            player_o=sample_players[1],
            current_player="X",
            next_board=4  # Must play in center board
        )
        self.start_game(active_game)
        
        # Try to play in board 0
        game, error = GameService.make_move(
            active_game.id,
            board_index=0,
            position=4,
            player_id=sample_players[0].id
        )
        
        assert error == "Must play in the indicated board"
        assert game is None

    @freeze_time("2024-01-01 12:00:00")
    def test_time_control_forfeit(self):
        """Test that a player forfeits when they exceed their time limit."""
        # TODO: implement this once we figure out how to manage clock better
        pass

    def test_win_with_forced_moves(self, sample_players):
        """Test complex scenario where next_board forces moves in specific pattern."""
        # Set up a scenario where player X can win by forcing O into bad positions
        boards = [[""]*9 for _ in range(9)]
        
        # X has won boards 0 and 4, needs board 8 for diagonal win
        boards[0] = ["X"]*3 + ["O"]*2 + [""]*4
        boards[4] = ["X"]*3 + ["O"]*2 + [""]*4
        
        # Board 8 is nearly won by X, needs one more move
        boards[8] = ["X", "X", "", "O", "O", "", "", "", ""]
        
        active_game = Game.create(
            player_x=sample_players[0],
            player_o=sample_players[1],
            current_player="X",
            next_board=8,  # Force play in board 8
            boards=json.dumps(boards)
        )
        self.start_game(active_game)
        
        # X makes winning move in board 8
        game, _ = GameService.make_move(
            active_game.id,
            board_index=8,
            position=2,
            player_id=sample_players[0].id
        )
        
        assert game.game_over
        assert game.winner == "X"
        
        # Check meta board state through the proper interface
        meta = game.get_meta_board()
        meta_state = meta.to_list()
        assert meta_state.count("X") == 3  # Three boards won

    def test_simultaneous_board_completion(self, sample_players):
        """Test edge case where a move completes both a small board and the meta board."""
        boards = [[""]*9 for _ in range(9)]
        
        # Set up two completed boards in a row for X
        for board_idx in [0, 1]:
            boards[board_idx] = ["X"]*3 + ["O"]*2 + [""]*4
        
        # Set up board 2 for a winning move
        boards[2] = ["X", "X", "", "O", "O", "", "", "", ""]
        
        active_game = Game.create(
            player_x=sample_players[0],
            player_o=sample_players[1],
            current_player="X",
            next_board=2,
            boards=json.dumps(boards)
        )
        self.start_game(active_game)
        
        # Make the move that completes both board 2 and the top row of meta board
        game, _ = GameService.make_move(
            active_game.id,
            board_index=2,
            position=2,
            player_id=sample_players[0].id
        )
        
        assert game.game_over
        assert game.winner == "X"
        
        # Check meta board state through the proper interface
        meta = game.get_meta_board()
        meta_state = meta.to_list()
        assert meta_state[0] == meta_state[1] == meta_state[2] == "X"

    def test_board_and_game_ties(self, sample_players):
        """Test that boards and games can end in ties and are properly reflected in meta board."""
        boards = [[""]*9 for _ in range(9)]
        
        # Set up a tied board (board 0)
        boards[0] = ["X", "O", "X",
                    "X", "O", "O",
                    "O", "X", "X"]  # Tied board
        
        # Set up a board that will be tied next (board 1)
        boards[1] = ["X", "O", "X",
                    "X", "O", "O",
                    "O", "X", ""]  # One move from tie
        
        now = datetime.now()
        active_game = Game.create(
            player_x=sample_players[0],
            player_o=sample_players[1],
            current_player="X",
            next_board=1,
            boards=json.dumps(boards),
            last_move_time=now,
            created_at=now
        )
        self.start_game(active_game)
        
        # Check that completed tied board shows as 'T'
        meta = active_game.get_meta_board()
        meta_state = meta.to_list()
        assert meta_state[0] == "T"  # First board should be marked as tied
        
        # Complete the second board to a tie
        game, _ = GameService.make_move(
            active_game.id,
            board_index=1,
            position=8,
            player_id=sample_players[0].id
        )
        
        # Verify the second board is now also marked as tied
        meta = game.get_meta_board()
        meta_state = meta.to_list()
        assert meta_state[1] == "T"  # Second board should now be tied
        assert meta_state.count("T") == 2  # Should have two tied boards 