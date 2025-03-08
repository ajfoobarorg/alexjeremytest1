import uuid
from datetime import datetime
import json
from typing import List, Optional, Tuple

from models import Game, Player
from board_logic import GameLogic

class PlayerService:
    @staticmethod
    def get_or_create_player(player_id: str, player_name: Optional[str] = None) -> Player:
        """Get an existing player or create a new one."""
        try:
            player = Player.get(Player.id == player_id)
            # Update name if provided and different from current name
            if player_name is not None and player.name != player_name:
                player.name = player_name
                player.save()
            return player
        except Player.DoesNotExist:
            # For new players, ensure we have a name (use empty string if none provided)
            name_to_use = player_name if player_name is not None else ""
            return Player.create(
                id=player_id,
                name=name_to_use
            )
    
    @staticmethod
    def update_player_stats(player_id: str, player_name: str, result: str) -> Player:
        """Update player stats after a game."""
        player = PlayerService.get_or_create_player(player_id, player_name)
        
        if result == 'win':
            player.wins += 1
        elif result == 'loss':
            player.losses += 1
        elif result == 'draw':
            player.draws += 1
        
        player.save()
        return player
    
    @staticmethod
    def update_player_name(player_id: str, name: str) -> bool:
        """Update a player's name."""
        try:
            player = PlayerService.get_or_create_player(player_id, name)
            return True
        except Exception as e:
            print(f"Error updating player name: {str(e)}")
            return False

class GameService:
    @staticmethod
    def create_game(player_id: str, player_name: str, game_name: str, is_public: bool) -> Game:
        """Create a new game."""
        # Ensure player exists
        player = PlayerService.get_or_create_player(player_id, player_name)
        
        game_id = str(uuid.uuid4())
        game = Game.create(
            id=game_id,
            name=game_name,
            current_player="X",
            next_board=None,
            created_at=datetime.now(),
            is_public=is_public,
            player_x=player,
            player_x_name=player_name
        )
        return game
    
    @staticmethod
    def get_game(game_id: str) -> Optional[Game]:
        """Get a game by ID."""
        try:
            return Game.get(Game.id == game_id)
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def get_public_games() -> List[Game]:
        """Get all public games that are not full."""
        return list(Game.select().where(
            (Game.is_public == True) & 
            (Game.player_o.is_null()) & 
            (Game.game_over == False)
        ))
    
    @staticmethod
    def join_game(game_id: str, player_id: str, player_name: str) -> Optional[Game]:
        """Join a game as player O."""
        try:
            game = Game.get(Game.id == game_id)
            
            if game.game_over:
                return None
            
            if game.player_o:
                return None
            
            # Ensure player exists
            player = PlayerService.get_or_create_player(player_id, player_name)
            
            # Check if player is trying to play against themselves
            if game.player_x.id == player.id:
                return None
            
            game.player_o = player
            game.player_o_name = player_name
            game.save()
            
            return game
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def start_game(game_id: str, player_id: str) -> Optional[Game]:
        """Start a game (player X only)."""
        try:
            game = Game.get(Game.id == game_id)
            
            if game.player_x.id != player_id:
                return None
                
            if not game.player_o:
                return None
                
            game.game_started = True
            game.last_move_time = datetime.now()
            game.save()
            
            return game
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def resign_game(game_id: str, player_id: str) -> Optional[Game]:
        """Resign from a game."""
        try:
            game = Game.get(Game.id == game_id)
            
            if (not game.player_x or game.player_x.id != player_id) and \
               (not game.player_o or game.player_o.id != player_id):
                return None
            
            # Set winner to the other player
            if game.player_x and game.player_x.id == player_id:
                game.winner = 'O'
                winner_id = game.player_o.id if game.player_o else None
                winner_name = game.player_o_name
                loser_id = player_id
                loser_name = game.player_x_name
            else:
                game.winner = 'X'
                winner_id = game.player_x.id if game.player_x else None
                winner_name = game.player_x_name
                loser_id = player_id
                loser_name = game.player_o_name
                
            game.game_over = True
            game.save()
            
            # Update player stats
            if winner_id:
                PlayerService.update_player_stats(winner_id, winner_name, 'win')
            if loser_id:
                PlayerService.update_player_stats(loser_id, loser_name, 'loss')
            
            return game
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def make_move(game_id: str, board_index: int, position: int, player_id: str) -> Tuple[Optional[Game], Optional[str]]:
        """Make a move in the game. Returns (game, error_message)."""
        try:
            game = Game.get(Game.id == game_id)
            
            # Verify it's the player's turn
            current_player = game.player_x if game.current_player == 'X' else game.player_o
            if not current_player or current_player.id != player_id:
                return None, "Not your turn"
                
            # Update time used and check if player ran out of time
            time_remaining = game.update_time_used()
            if time_remaining <= 0:
                # Player ran out of time, they lose
                game.winner = 'O' if game.current_player == 'X' else 'X'
                game.game_over = True
                game.save()
                
                # Update player stats
                if game.winner == 'X' and game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_x.id, game.player_x_name, 'win')
                    PlayerService.update_player_stats(game.player_o.id, game.player_o_name, 'loss')
                elif game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_o.id, game.player_o_name, 'win')
                    PlayerService.update_player_stats(game.player_x.id, game.player_x_name, 'loss')
                
                return game, None
            
            # Verify the move is in the correct board
            if game.next_board is not None and game.next_board != board_index:
                return None, "Must play in the indicated board"
            
            # Get boards from JSON
            boards = json.loads(game.boards)
            meta_board = json.loads(game.meta_board)
            
            # Verify the move is valid
            if meta_board[board_index] != "":
                return None, "Board already completed"
                
            if boards[board_index][position] != "":
                return None, "Position already taken"
            
            # Make the move
            boards[board_index][position] = game.current_player
            
            # Check if the small board was won
            board_winner = GameLogic.check_winner(boards[board_index])
            if board_winner:
                meta_board[board_index] = board_winner
            # Check if the small board is full (tie)
            elif GameLogic.is_board_full(boards[board_index]):
                meta_board[board_index] = "T"  # T for Tie
            
            # Update game state
            game.boards = json.dumps(boards)
            game.meta_board = json.dumps(meta_board)
            
            # Check if the move resulted in a win on the meta board
            meta_winner = GameLogic.check_winner(meta_board)
            if meta_winner:
                game.winner = meta_winner
                game.game_over = True
                game.save()
                
                # Update player stats
                if game.winner == 'X' and game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_x.id, game.player_x_name, 'win')
                    PlayerService.update_player_stats(game.player_o.id, game.player_o_name, 'loss')
                elif game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_o.id, game.player_o_name, 'win')
                    PlayerService.update_player_stats(game.player_x.id, game.player_x_name, 'loss')
                
                return game, None
                
            # Check if the meta board is full (draw)
            if GameLogic.is_board_full(meta_board):
                game.game_over = True
                game.save()
                
                # Update player stats for a draw
                if game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_x.id, game.player_x_name, 'draw')
                    PlayerService.update_player_stats(game.player_o.id, game.player_o_name, 'draw')
                
                return game, None
            
            # Set next board based on the position played
            # If the target board is completed, player can choose any incomplete board
            if meta_board[position] != "" or GameLogic.is_board_full(boards[position]):
                game.next_board = None
            else:
                game.next_board = position
            
            # Switch player
            game.current_player = "O" if game.current_player == "X" else "X"
            
            game.save()
            return game, None
            
        except Game.DoesNotExist:
            return None, "Game not found" 