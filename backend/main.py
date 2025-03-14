from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import datetime

from config import config
from models import initialize_db
from schemas import (
    PlayerNameUpdate, PlayerResponse, MatchmakingRequest, MatchmakingResponse,
    GameResponse
)
from services import GameService, PlayerService
from matchmaking import MatchmakingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Log CORS configuration
logger.info(f"Setting up CORS with allow_origins: {config.ALLOWED_ORIGINS}")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
initialize_db()

@app.get("/")
def read_root():
    return {"message": "Ultimate Tic-Tac-Toe API"}

@app.get("/games/{game_id}")
async def get_game(game_id: str):
    game = GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

@app.get("/players/{player_id}")
async def get_player(player_id: str):
    player = PlayerService.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerResponse.model_validate(player)

@app.post("/players/{player_id}/name")
async def update_player_name(player_id: str, request: PlayerNameUpdate):
    success = PlayerService.update_player_name(player_id, request.name)
    if not success:
        raise HTTPException(status_code=400, detail="Could not update player name")
    return {"success": True}

# Matchmaking endpoints
@app.post("/matchmaking/join")
async def join_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Join the matchmaking queue"""
    if not MatchmakingService.add_player(request.player_id):
        raise HTTPException(status_code=400, detail="Could not add player to matchmaking")
    return MatchmakingResponse(status="waiting")

@app.post("/matchmaking/ping")
async def ping_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Ping to check matchmaking status and keep player in queue"""
    # Update player's presence
    MatchmakingService.update_ping(request.player_id)
    
    # Check for match
    game, error, opponent_name, match_accepted = MatchmakingService.find_match(request.player_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if game:
        # Both players have accepted, return game ID
        return MatchmakingResponse(
            status="matched",
            game_id=game.id,
            opponent_name=opponent_name
        )
    elif opponent_name:
        # Match found but waiting for acceptance
        return MatchmakingResponse(
            status="waiting_acceptance",
            opponent_name=opponent_name
        )
    else:
        # Still waiting for match
        return MatchmakingResponse(status="waiting")

@app.post("/matchmaking/cancel")
async def cancel_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Cancel matchmaking for a player"""
    if MatchmakingService.remove_player(request.player_id):
        return MatchmakingResponse(status="cancelled")
    raise HTTPException(status_code=400, detail="Player not in matchmaking")

# Game action endpoints
@app.post("/games/{game_id}/move/{board_index}/{position}")
async def make_move(game_id: str, board_index: int, position: int, player_id: str):
    game, error = GameService.make_move(game_id, board_index, position, player_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

@app.post("/games/{game_id}/resign")
async def resign_game(game_id: str, player_id: str):
    game = GameService.resign_game(game_id, player_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

@app.post("/games/{game_id}/ready")
async def ready_game(game_id: str, player_id: str) -> GameResponse:
    """Signal that player X is ready to start the game"""
    game = GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Only player X can signal ready
    if game.player_x.id != player_id:
        raise HTTPException(status_code=400, detail="Only player X can signal ready")
    
    # Start the game by setting the initial last_move_time
    game.last_move_time = datetime.datetime.now()
    game.save()
    
    return GameResponse(**game.to_dict()) 