from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import config
from models import initialize_db
from schemas import (
    PlayerNameUpdate, PlayerResponse, MatchmakingRequest, MatchmakingResponse
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
    success = MatchmakingService.add_player(request.player_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not add player to matchmaking")
    return MatchmakingResponse(status="waiting")

@app.post("/matchmaking/ping")
async def ping_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    game, error = MatchmakingService.find_match(request.player_id)
    
    if error:
        return MatchmakingResponse(
            status="error",
            message=error
        )
    
    if game:
        return MatchmakingResponse(
            status="matched",
            game=GameResponse.model_validate(game)
        )
    
    # Update ping time
    if not MatchmakingService.update_ping(request.player_id):
        return MatchmakingResponse(
            status="error",
            message="Player not in waiting list"
        )
    
    return MatchmakingResponse(status="waiting")

@app.post("/matchmaking/cancel")
async def cancel_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    success = MatchmakingService.remove_player(request.player_id)
    if not success:
        raise HTTPException(status_code=400, detail="Player not in matchmaking")
    return MatchmakingResponse(status="cancelled")

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