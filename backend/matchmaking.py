# Standard library imports
import datetime
import logging
import time
import random
from typing import Dict, List, Tuple, Optional, Set

# Local imports
from models import Player, Game
from services import GameService, PlayerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchmakingService:
    """Service for handling matchmaking between players."""
    
    # In-memory matchmaking state
    _matchmaking_players: Dict[str, float] = {}  # player_id -> last_ping_time
    _pending_matches: Dict[str, Tuple[str, str, float]] = {}  # player_id -> (opponent_id, game_id, created_at)
    _blacklisted_pairs: Set[Tuple[str, str]] = set()  # (player_id, player_id) pairs that rejected matching
    
    # Constants
    MATCH_ACCEPTANCE_TIMEOUT = 15  # seconds
    PING_TIMEOUT = 10  # seconds
    
    @classmethod
    def add_player(cls, player_id: str) -> bool:
        """Add a player to the matchmaking queue.
        
        Args:
            player_id: The ID of the player to add.
            
        Returns:
            True if player was added, False otherwise.
        """
        # Make sure player exists
        player = PlayerService.get_player(player_id)
        if not player:
            logger.error(f"Cannot add player {player_id} to matchmaking: player not found")
            return False
        
        # Add player if not already in queue
        if player_id not in cls._matchmaking_players:
            logger.info(f"Adding player {player.username} ({player_id}) to matchmaking")
            cls._matchmaking_players[player_id] = time.time()
            return True
        
        # Already in queue, just update ping time
        cls._matchmaking_players[player_id] = time.time()
        return True
    
    @classmethod
    def remove_player(cls, player_id: str) -> bool:
        """Remove a player from the matchmaking queue.
        
        Args:
            player_id: The ID of the player to remove.
            
        Returns:
            True if player was removed, False if player wasn't in queue.
        """
        if player_id in cls._matchmaking_players:
            del cls._matchmaking_players[player_id]
            logger.info(f"Removed player {player_id} from matchmaking")
            return True
        
        # Also remove from pending matches if present
        if player_id in cls._pending_matches:
            opponent_id, game_id, _ = cls._pending_matches[player_id]
            
            # Also remove opponent's pending match
            if opponent_id in cls._pending_matches:
                del cls._pending_matches[opponent_id]
            
            del cls._pending_matches[player_id]
            logger.info(f"Removed player {player_id} and pending match with {opponent_id}")
        
        return False
    
    @classmethod
    def update_ping(cls, player_id: str) -> None:
        """Update the last ping time for a player.
        
        Args:
            player_id: The ID of the player to update.
        """
        if player_id in cls._matchmaking_players:
            cls._matchmaking_players[player_id] = time.time()
    
    @classmethod
    def cleanup_inactive_players(cls) -> None:
        """Remove players who haven't pinged recently."""
        # Implementation of cleanup_inactive_players method
        pass
    
    @classmethod
    def cleanup_expired_matches(cls) -> None:
        """Remove match proposals that have expired without acceptance."""
        # Implementation of cleanup_expired_matches method
        pass
    
    @classmethod
    def find_match(cls, player_id: str) -> Tuple[Optional[Game], Optional[str], Optional[str], bool]:
        """Find a match for a player or return an existing pending match.
        
        Args:
            player_id: The ID of the player to find a match for.
            
        Returns:
            A tuple of (game, error_message, opponent_name, accepted_flag).
        """
        # Implementation of find_match method
        pass
    
    @classmethod
    def get_eligible_opponents(cls, player_id: str) -> List[str]:
        """Get a list of eligible opponent IDs for a player.
        
        Args:
            player_id: The ID of the player to find opponents for.
            
        Returns:
            A list of eligible opponent player IDs.
        """
        # Implementation of get_eligible_opponents method
        pass
    
    @classmethod
    def create_match(cls, player_id: str, opponent_id: str) -> Tuple[Game, str]:
        """Create a pending match between two players.
        
        Args:
            player_id: The ID of the first player.
            opponent_id: The ID of the second player.
            
        Returns:
            A tuple of (game, opponent_name).
        """
        # Implementation of create_match method
        pass

    @staticmethod
    def create_game(player1: Player, player2: Player) -> Game:
        """Create a new game with randomly assigned X and O players"""
        # Randomly assign X and O
        if random.random() < 0.5:
            player_x, player_o = player1, player2
        else:
            player_x, player_o = player2, player1
        
        return GameService.create_game(player_x, player_o)

    @staticmethod
    def is_player_in_queue(player_id: str) -> bool:
        """Check if a player is in the waiting queue."""
        return player_id in MatchmakingService._matchmaking_players

    @staticmethod
    def has_pending_match(player_id: str) -> bool:
        """Check if a player has a pending match."""
        return player_id in MatchmakingService._pending_matches 