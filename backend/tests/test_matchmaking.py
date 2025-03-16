import pytest
import json
from datetime import datetime, timedelta
from freezegun import freeze_time
from matchmaking import MatchmakingService
from models import Game, Player

@pytest.mark.matchmaking
class TestMatchmaking:
    @freeze_time("2024-01-01 12:00:00")
    def test_ttl_expiration(self):
        """Test that matchmaking entries expire after TTL."""
        # TODO: implement this once we figure out how to manage clock better


    def test_concurrent_matchmaking(self, sample_players):
        """Test that multiple players can be matched correctly."""
        # Clear any existing entries
        MatchmakingService.waiting_players.clear()
        MatchmakingService.matched_games.clear()
        
        # Add first player
        MatchmakingService.add_player(sample_players[0].id)
        
        # Add second player and get match result
        MatchmakingService.add_player(sample_players[1].id)
        game, error, opponent_name, accepted = MatchmakingService.find_match(sample_players[0].id)
        
        assert opponent_name == "test_player_1"  # This is the username from sample_players fixture
        assert not accepted  # Match needs acceptance from both players
        
        # Verify both players are removed from waiting list
        assert not MatchmakingService.is_player_in_queue(sample_players[0].id)
        assert not MatchmakingService.is_player_in_queue(sample_players[1].id)

    @freeze_time("2024-01-01 12:00:00")
    def test_match_acceptance_timeout(self):
        """Test that matches expire if not accepted in time."""
        player1 = Player.create(
            username="player1",
            email="player1@test.com"
        )
        player2 = Player.create(
            username="player2",
            email="player2@test.com"
        )
        
        # Add both players to matchmaking
        MatchmakingService.add_player(player1.id)
        MatchmakingService.add_player(player2.id)
        
        # Advance time past acceptance timeout
        with freeze_time("2024-01-01 12:00:31"):
            # Check that match is no longer pending
            assert not MatchmakingService.has_pending_match(player1.id)
            assert not MatchmakingService.has_pending_match(player2.id)

    def test_player_cancellation(self, sample_players):
        """Test that cancelling matchmaking properly cleans up both players."""
        # Clear any existing entries
        MatchmakingService.waiting_players.clear()
        MatchmakingService.matched_games.clear()
        
        # Add both players
        MatchmakingService.add_player(sample_players[0].id)
        MatchmakingService.add_player(sample_players[1].id)
        
        # Get match
        _, _, opponent_name, _ = MatchmakingService.find_match(sample_players[0].id)
        assert opponent_name == "test_player_1"  # Using the correct username from sample_players
        
        # Cancel matchmaking for player 1
        MatchmakingService.remove_player(sample_players[0].id)
        
        # Verify both players are removed from matched games
        assert sample_players[0].id not in MatchmakingService.matched_games
        assert sample_players[1].id not in MatchmakingService.matched_games

    @freeze_time("2024-01-01 12:00:00")
    def test_multiple_acceptance_required(self, sample_players):
        """Test that both players must accept before game starts."""
        # TODO: write a good test for thisClear any existing entries

    @freeze_time("2024-01-01 12:00:00")
    def test_rejoin_after_timeout(self):
        """Test that players can rejoin after their previous entry times out."""
        player = Player.create(
            username="test_player",
            email="test_player@test.com"
        )
        
        # First matchmaking attempt
        MatchmakingService.add_player(player.id)
        
        # Advance time past TTL
        with freeze_time("2024-01-01 12:00:31"):
            # Player should be able to rejoin
            MatchmakingService.add_player(player.id)
            assert MatchmakingService.is_player_in_queue(player.id) 