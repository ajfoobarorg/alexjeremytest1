# Standard library imports
import json
import math
from typing import Optional, Tuple

# Local imports
from models import Game, Player
from board_logic import MetaBoard
from schemas import PlayerLevel

# Starting ELO ratings for different player levels
LEVEL_ELO_RATINGS = {
    PlayerLevel.NEW: 200,
    PlayerLevel.BEGINNER: 400,
    PlayerLevel.INTERMEDIATE: 700,
    PlayerLevel.ADVANCED: 900
}

class PlayerService:
    """Service for player-related operations."""
    
    @staticmethod
    def get_player(player_id: str) -> Optional[Player]:
        """Get a player by ID.
        
        Args:
            player_id: The ID of the player to retrieve.
            
        Returns:
            The player object if found, None otherwise.
        """
        try:
            return Player.get(Player.id == player_id)
        except Player.DoesNotExist:
            return None
    
    @staticmethod
    def calculate_elo_change(player_elo: int, opponent_elo: int, result: float, k_factor: int = 32) -> int:
        """Calculate ELO rating change.
        
        Args:
            player_elo: Current ELO rating of the player.
            opponent_elo: Current ELO rating of the opponent.
            result: 1.0 for win, 0.5 for draw, 0.0 for loss.
            k_factor: K-factor for ELO calculation (default: 32).
            
        Returns:
            The change in ELO rating (positive or negative).
        """
        # Calculate expected score
        expected_score = 1 / (1 + math.pow(10, (opponent_elo - player_elo) / 400))
        
        # Calculate ELO change
        elo_change = round(k_factor * (result - expected_score))
        
        return elo_change
    
    @staticmethod
    def update_player_elo(player_id: str, opponent_id: str, result: str) -> Tuple[Player, int]:
        """Update player's ELO rating after a game.
        
        Args:
            player_id: The ID of the player to update.
            opponent_id: The ID of the opponent.
            result: The result of the game ('win', 'loss', or 'draw').
            
        Returns:
            A tuple containing the updated player object and the ELO change.
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
        """Update player's win/loss/draw statistics.
        
        Args:
            player_id: The ID of the player to update.
            result: The result of the game ('win', 'loss', or 'draw').
            
        Returns:
            The updated player object.
        """
        player = PlayerService.get_player(player_id)
        
        if result == 'win':
            player.wins += 1
        elif result == 'loss':
            player.losses += 1
        elif result == 'draw':
            player.draws += 1
        
        player.save()
        return player
    
class ProfileService:
    """Service for player profile operations."""
    
    @staticmethod
    def get_profile(player_id: str) -> Optional[Player]:
        """Get a player's profile by ID.
        
        Args:
            player_id: The ID of the player to retrieve.
            
        Returns:
            The player object if found, None otherwise.
        """
        try:
            return Player.get(Player.id == player_id)
        except Player.DoesNotExist:
            return None
    
    @staticmethod
    def get_profile_by_email(email: str) -> Optional[Player]:
        """Get a player's profile by email.
        
        Args:
            email: The email of the player to retrieve.
            
        Returns:
            The player object if found, None otherwise.
        """
        try:
            return Player.get(Player.email == email)
        except Player.DoesNotExist:
            return None
    
    @staticmethod
    def create_profile(username: str, email: str, level: str, timezone: Optional[str] = None, country: Optional[str] = None) -> Player:
        """Create a new player profile.
        
        Args:
            username: The username for the new player.
            email: The email for the new player.
            level: The skill level of the new player.
            timezone: The timezone of the new player (optional).
            country: The country code of the new player (optional).
            
        Returns:
            The newly created player object.
        """
        return Player.create(
            username=username,
            email=email,
            level=level,
            timezone=timezone,
            country=country,
            elo=LEVEL_ELO_RATINGS[level]
        )
    
    @staticmethod
    def update_profile(player_id: str, **update_data) -> Optional[Player]:
        """Update a player's profile.
        
        Args:
            player_id: The ID of the player to update.
            **update_data: Dictionary of fields to update.
            
        Returns:
            The updated player object if found, None otherwise.
        """
        try:
            player = Player.get(Player.id == player_id)
            for field, value in update_data.items():
                if hasattr(player, field) and value is not None:
                    setattr(player, field, value)
            player.save()
            return player
        except Player.DoesNotExist:
            return None
    
    @staticmethod
    def check_username_exists(username: str) -> bool:
        """Check if a username is already taken.
        
        Args:
            username: The username to check.
            
        Returns:
            True if the username exists, False otherwise.
        """
        return Player.select().where(Player.username == username).exists()
    
    @staticmethod
    def check_email_exists(email: str) -> bool:
        """Check if an email is already registered.
        
        Args:
            email: The email to check.
            
        Returns:
            True if the email exists, False otherwise.
        """
        return Player.select().where(Player.email == email).exists()

class GameService:
    """Service for game-related operations."""
    
    @staticmethod
    def create_game(player_x: Player, player_o: Player) -> Game:
        """Create a new game between two players.
        
        Args:
            player_x: The player who will play as X.
            player_o: The player who will play as O.
            
        Returns:
            The newly created game object.
        """
        game = Game.create(
            player_x=player_x,
            player_o=player_o
        )
        return game
  
    @staticmethod
    def get_game(game_id: str) -> Optional[Game]:
        """Get a game by ID.
        
        Args:
            game_id: The ID of the game to retrieve.
            
        Returns:
            The game object if found, None otherwise.
        """
        try:
            return Game.get(Game.id == game_id)
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def resign_game(game_id: str, player_id: str) -> Optional[Game]:
        """Handle a player resigning from a game.
        
        Args:
            game_id: The ID of the game.
            player_id: The ID of the player resigning.
            
        Returns:
            The updated game object if found, None otherwise.
        """
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
        """Make a move in a game.
        
        Args:
            game_id: The ID of the game.
            board_index: The index of the board (0-8).
            position: The position on the board (0-8).
            player_id: The ID of the player making the move.
            
        Returns:
            A tuple containing the updated game object (or None) and an error message (or None).
        """
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
                
                return game, "Time control exceeded - game forfeited"
            
            # Verify the move is in the correct board
            if game.next_board is not None and game.next_board != board_index:
                return None, "Must play in the indicated board"
            
            # Get boards as proper Board objects
            boards = game.get_boards()
            
            # Get meta state as proper MetaBoard object
            meta = game.get_meta_board()
            
            # Verify the move is valid
            if not meta.is_board_playable(board_index):
                return None, "Board already completed"
                
            if boards[board_index].get(position) != "":
                return None, "Position already taken"
            
            # Make the move
            boards[board_index].set(position, game.current_player)
            
            # Save boards
            game.set_boards(boards)
            
            # Check for winner using new meta state
            meta = game.get_meta_board()  # Recompute after move
            meta_winner = meta.get_winner()
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
                
            # Check for draw
            if meta.is_full():
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
            
            # Set next board
            if not meta.is_board_playable(position):
                game.next_board = None
            else:
                game.next_board = position
            
            # Switch player
            game.current_player = "O" if game.current_player == "X" else "X"
            
            game.save()
            return game, None
            
        except Game.DoesNotExist:
            return None, "Game not found" 