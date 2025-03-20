# Standard library
import logging
import random
from threading import Lock
from typing import Optional, Tuple

# Third-party
from cachetools import TTLCache

# Local
from models import Game, Player
from services import ProfileService, GameService

class MatchmakingService:
    # TTL of 30 seconds for waiting players and matches
    CACHE_TTL = 30
    # Thread lock for synchronization
    lock = Lock()
    # TTL cache for waiting players
    waiting_players = TTLCache(maxsize=1000, ttl=CACHE_TTL)
    # TTL cache for matched games
    matched_games = TTLCache(maxsize=1000, ttl=CACHE_TTL)  # player_id -> (game_id, opponent_name, accepted)
    
    @staticmethod
    def add_player(player_id: str) -> bool:
        """Add a player to the waiting list"""
        player = ProfileService.get_profile(player_id)
        if not player:
            return False
        
        with MatchmakingService.lock:
            # Don't add if player is already waiting
            if player_id in MatchmakingService.waiting_players:
                return True
            # Clear any previous matched game
            if player_id in MatchmakingService.matched_games:
                del MatchmakingService.matched_games[player_id]
            logging.info(f"Adding player {player_id} to waiting list")
            MatchmakingService.waiting_players[player_id] = player
        return True
    
    @staticmethod
    def remove_player(player_id: str) -> bool:
        """Remove a player from the waiting list and matched games"""
        with MatchmakingService.lock:
            was_waiting = player_id in MatchmakingService.waiting_players
            was_matched = player_id in MatchmakingService.matched_games
            
            if player_id in MatchmakingService.waiting_players:
                del MatchmakingService.waiting_players[player_id]
            if player_id in MatchmakingService.matched_games:
                # Get the game info to clean up the other player's match
                game_id, _, _ = MatchmakingService.matched_games[player_id]
                # Find and remove the other player's match
                for other_id, (other_game_id, _, _) in list(MatchmakingService.matched_games.items()):
                    if other_game_id == game_id and other_id != player_id:
                        del MatchmakingService.matched_games[other_id]
                        break
                del MatchmakingService.matched_games[player_id]
                
            return was_waiting or was_matched
    
    @staticmethod
    def update_ping(player_id: str) -> bool:
        """Update the player's presence in the cache (refreshes TTL)"""
        with MatchmakingService.lock:
            if player_id in MatchmakingService.waiting_players:
                player = MatchmakingService.waiting_players[player_id]
                # Re-add to refresh TTL
                MatchmakingService.waiting_players[player_id] = player
                return True
            elif player_id in MatchmakingService.matched_games:
                # Refresh TTL for matched game and mark as accepted
                game_id, opponent_name, _ = MatchmakingService.matched_games[player_id]
                MatchmakingService.matched_games[player_id] = (game_id, opponent_name, True)
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
        
        return GameService.create_game(player_x, player_o)
    
    @staticmethod
    def find_match(player_id: str) -> Tuple[Optional[Game], Optional[str], Optional[str], Optional[bool]]:
        """Find a match for the player. Returns (game, error_message, opponent_name, match_accepted)"""
        with MatchmakingService.lock:
            # First check if player has a matched game
            if player_id in MatchmakingService.matched_games:
                game_id, opponent_name, accepted = MatchmakingService.matched_games[player_id]
                
                # Check if both players have accepted
                both_accepted = accepted
                if both_accepted:
                    for other_id, (other_game_id, _, other_accepted) in MatchmakingService.matched_games.items():
                        if other_game_id == game_id and other_id != player_id:
                            both_accepted = both_accepted and other_accepted
                            break
                
                if both_accepted:
                    # Both players have accepted, clean up and start the game
                    logging.info(f"Both players have accepted, cleaning up and starting game {game_id}")
                    del MatchmakingService.matched_games[player_id]
                    game = Game.get(Game.id == game_id)
                    if not game:
                        logging.error(f"Game {game_id} not found after both players have accepted")
                        return None, "Game not found", None, None
                    return game, None, opponent_name, True
                else:
                    # Still waiting for other player to accept
                    return None, None, opponent_name, False
            
            # Check if player is still in waiting list
            if player_id not in MatchmakingService.waiting_players:
                return None, "Player not in waiting list", None, None
                
            player = MatchmakingService.waiting_players[player_id]
            # Refresh TTL
            MatchmakingService.waiting_players[player_id] = player
            
            # If there's only one player (this one), no match yet
            if len(MatchmakingService.waiting_players) <= 1:
                return None, None, None, None
            
            # Find another player
            for other_id, other_player in list(MatchmakingService.waiting_players.items()):
                if other_id != player_id:
                    try:
                        # Create the game
                        game = MatchmakingService.create_game(player, other_player)
                        logging.info(f"Created game {game.id} between {player.username} and {other_player.username}")
                        
                        # Store the game ID and opponent names for both players
                        MatchmakingService.matched_games[player_id] = (game.id, other_player.username, False)
                        MatchmakingService.matched_games[other_id] = (game.id, player.username, False)
                        
                        # Remove both players from waiting list
                        del MatchmakingService.waiting_players[player_id]
                        del MatchmakingService.waiting_players[other_id]
                        
                        return None, None, other_player.username, False
                    except Exception as e:
                        return None, f"Error creating game: {str(e)}", None, None
            
            return None, None, None, None 

    @staticmethod
    def is_player_in_queue(player_id: str) -> bool:
        """Check if a player is in the waiting queue."""
        MatchmakingService.waiting_players.expire()
        return player_id in MatchmakingService.waiting_players

    @staticmethod
    def has_pending_match(player_id: str) -> bool:
        """Check if a player has a pending match."""
        MatchmakingService.matched_games.expire()
        return player_id in MatchmakingService.matched_games 