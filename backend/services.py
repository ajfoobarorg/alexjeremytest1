import uuid
from datetime import datetime
import json
from typing import List, Optional, Tuple
import math

from models import Game, Player
from board_logic import GameLogic

class PlayerService:
    @staticmethod
    def get_player(player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        try:
            return Player.get(Player.id == player_id)
        except Player.DoesNotExist:
            return None
    
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
    def calculate_elo_change(player_elo: int, opponent_elo: int, result: float, k_factor: int = 32) -> int:
        """
        Calculate ELO rating change.
        
        Args:
            player_elo: Current ELO rating of the player
            opponent_elo: Current ELO rating of the opponent
            result: 1.0 for win, 0.5 for draw, 0.0 for loss
            k_factor: K-factor for ELO calculation (default: 32)
            
        Returns:
            The change in ELO rating (positive or negative)
        """
        # Calculate expected score
        expected_score = 1 / (1 + math.pow(10, (opponent_elo - player_elo) / 400))
        
        # Calculate ELO change
        elo_change = round(k_factor * (result - expected_score))
        
        return elo_change
    
    @staticmethod
    def update_player_elo(player_id: str, opponent_id: str, result: str) -> Tuple[Player, int]:
        """
        Update player's ELO rating based on game result.
        
        Args:
            player_id: ID of the player
            opponent_id: ID of the opponent
            result: 'win', 'loss', or 'draw'
            
        Returns:
            Tuple of (updated player object, ELO change)
        """
        player = Player.get(Player.id == player_id)
        opponent = Player.get(Player.id == opponent_id)
        
        # Convert result to numerical value for ELO calculation
        result_value = 1.0 if result == 'win' else 0.0 if result == 'loss' else 0.5
        
        # Calculate ELO change
        elo_change = PlayerService.calculate_elo_change(player.elo, opponent.elo, result_value)
        
        # Update player's ELO
        player.elo += elo_change
        player.save()
        
        return player, elo_change
    
    @staticmethod
    def update_player_stats(player_id: str, result: str) -> Player:
        """Update player stats after a game."""
        player = PlayerService.get_or_create_player(player_id)
        
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
            PlayerService.get_or_create_player(player_id, name)
            return True
        except Exception as e:
            print(f"Error updating player name: {str(e)}")
            return False

class GameService:
    @staticmethod
    def get_game(game_id: str) -> Optional[Game]:
        """Get a game by ID."""
        try:
            return Game.get(Game.id == game_id)
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
                loser_id = player_id
            else:
                game.winner = 'X'
                winner_id = game.player_x.id if game.player_x else None
                loser_id = player_id
                
            game.game_over = True
            game.save()
            
            # Update player stats
            if winner_id and loser_id:
                PlayerService.update_player_stats(winner_id, 'win')
                PlayerService.update_player_stats(loser_id, 'loss')
                
                # Update ELO ratings
                winner_player, winner_elo_change = PlayerService.update_player_elo(winner_id, loser_id, 'win')
                loser_player, loser_elo_change = PlayerService.update_player_elo(loser_id, winner_id, 'loss')
                
                # Store ELO changes in the game
                if game.winner == 'X':
                    game.player_x_elo_change = winner_elo_change
                    game.player_o_elo_change = loser_elo_change
                else:
                    game.player_x_elo_change = loser_elo_change
                    game.player_o_elo_change = winner_elo_change
                
                game.save()
            
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
                    PlayerService.update_player_stats(game.player_x.id, 'win')
                    PlayerService.update_player_stats(game.player_o.id, 'loss')
                    
                    # Update ELO ratings
                    player_x, x_elo_change = PlayerService.update_player_elo(game.player_x.id, game.player_o.id, 'win')
                    player_o, o_elo_change = PlayerService.update_player_elo(game.player_o.id, game.player_x.id, 'loss')
                    
                    # Store ELO changes
                    game.player_x_elo_change = x_elo_change
                    game.player_o_elo_change = o_elo_change
                    game.save()
                elif game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_o.id, 'win')
                    PlayerService.update_player_stats(game.player_x.id, 'loss')
                    
                    # Update ELO ratings
                    player_o, o_elo_change = PlayerService.update_player_elo(game.player_o.id, game.player_x.id, 'win')
                    player_x, x_elo_change = PlayerService.update_player_elo(game.player_x.id, game.player_o.id, 'loss')
                    
                    # Store ELO changes
                    game.player_x_elo_change = x_elo_change
                    game.player_o_elo_change = o_elo_change
                    game.save()
                
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
                    PlayerService.update_player_stats(game.player_x.id, 'win')
                    PlayerService.update_player_stats(game.player_o.id, 'loss')
                    
                    # Update ELO ratings
                    player_x, x_elo_change = PlayerService.update_player_elo(game.player_x.id, game.player_o.id, 'win')
                    player_o, o_elo_change = PlayerService.update_player_elo(game.player_o.id, game.player_x.id, 'loss')
                    
                    # Store ELO changes
                    game.player_x_elo_change = x_elo_change
                    game.player_o_elo_change = o_elo_change
                    game.save()
                elif game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_o.id, 'win')
                    PlayerService.update_player_stats(game.player_x.id, 'loss')
                    
                    # Update ELO ratings
                    player_o, o_elo_change = PlayerService.update_player_elo(game.player_o.id, game.player_x.id, 'win')
                    player_x, x_elo_change = PlayerService.update_player_elo(game.player_x.id, game.player_o.id, 'loss')
                    
                    # Store ELO changes
                    game.player_x_elo_change = x_elo_change
                    game.player_o_elo_change = o_elo_change
                    game.save()
                
                return game, None
                
            # Check if the meta board is full (draw)
            if GameLogic.is_board_full(meta_board):
                game.game_over = True
                game.save()
                
                # Update player stats for a draw
                if game.player_x and game.player_o:
                    PlayerService.update_player_stats(game.player_x.id, 'draw')
                    PlayerService.update_player_stats(game.player_o.id, 'draw')
                    
                    # Update ELO ratings for a draw
                    player_x, x_elo_change = PlayerService.update_player_elo(game.player_x.id, game.player_o.id, 'draw')
                    player_o, o_elo_change = PlayerService.update_player_elo(game.player_o.id, game.player_x.id, 'draw')
                    
                    # Store ELO changes
                    game.player_x_elo_change = x_elo_change
                    game.player_o_elo_change = o_elo_change
                    game.save()
                
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