from cachetools import TTLCache
from threading import Lock
import random
from datetime import datetime
import uuid
from typing import Optional, Tuple

from models import Game, Player
from services import PlayerService

class MatchmakingService:
    # TTL of 30 seconds for waiting players
    CACHE_TTL = 30
    # Thread lock for synchronization
    lock = Lock()
    # TTL cache for waiting players
    waiting_players = TTLCache(maxsize=1000, ttl=CACHE_TTL)
    
    @staticmethod
    def add_player(player_id: str) -> bool:
        """Add a player to the waiting list"""
        player = PlayerService.get_player(player_id)
        if not player:
            return False
        
        with MatchmakingService.lock:
            # Don't add if player is already waiting
            if player_id in MatchmakingService.waiting_players:
                return True
                
            MatchmakingService.waiting_players[player_id] = player
        return True
    
    @staticmethod
    def remove_player(player_id: str) -> bool:
        """Remove a player from the waiting list"""
        with MatchmakingService.lock:
            if player_id in MatchmakingService.waiting_players:
                del MatchmakingService.waiting_players[player_id]
                return True
        return False
    
    @staticmethod
    def update_ping(player_id: str) -> bool:
        """Update the player's presence in the cache (refreshes TTL)"""
        with MatchmakingService.lock:
            if player_id in MatchmakingService.waiting_players:
                player = MatchmakingService.waiting_players[player_id]
                # Re-add to refresh TTL
                MatchmakingService.waiting_players[player_id] = player
                return True
        return False
    
    @staticmethod
    def create_game(player1: Player, player2: Player) -> Game:
        """Create a new game with randomly assigned X and O players"""
        # Randomly assign X and O
        if random.random() < 0.5:
            player_x, player_o = player1, player2
        else:
            player_x, player_o = player2, player1
        
        game_id = str(uuid.uuid4())
        game = Game.create(
            id=game_id,
            name=f"Game: {player_x.name} vs {player_o.name}",
            current_player="X",
            next_board=None,
            created_at=datetime.now(),
            player_x=player_x,
            player_o=player_o
        )
        return game
    
    @staticmethod
    def find_match(player_id: str) -> Tuple[Optional[Game], Optional[str]]:
        """Find a match for the player. Returns (game, error_message)"""
        with MatchmakingService.lock:
            # Check if player is still in waiting list
            if player_id not in MatchmakingService.waiting_players:
                return None, "Player not in waiting list"
                
            player = MatchmakingService.waiting_players[player_id]
            # Refresh TTL
            MatchmakingService.waiting_players[player_id] = player
            
            # If there's only one player (this one), no match yet
            if len(MatchmakingService.waiting_players) <= 1:
                return None, None
            
            # Find another player
            for other_id, other_player in list(MatchmakingService.waiting_players.items()):
                if other_id != player_id:
                    try:
                        # Create the game
                        game = MatchmakingService.create_game(player, other_player)
                        
                        # Remove both players from waiting list
                        del MatchmakingService.waiting_players[player_id]
                        del MatchmakingService.waiting_players[other_id]
                        
                        return game, None
                    except Exception as e:
                        return None, f"Error creating game: {str(e)}"
            
            return None, None 