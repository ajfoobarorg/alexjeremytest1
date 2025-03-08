from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import config
from models import initialize_db
from schemas import (
    GameCreate, JoinGameRequest, PlayerNameUpdate, PlayerResponse
)
from services import GameService, PlayerService

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

@app.post("/games/new")
async def create_game(request: GameCreate):
    game = GameService.create_game(
        player_id=request.player_id,
        player_name=request.player_name,
        game_name=request.game_name,
        is_public=request.is_public
    )
    return game.to_dict()

@app.get("/games/public")
async def get_public_games():
    games = GameService.get_public_games()
    return [game.to_dict() for game in games]

@app.get("/games/{game_id}")
async def get_game(game_id: str):
    game = GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

@app.post("/games/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    game = GameService.join_game(
        game_id=game_id,
        player_id=request.player_id,
        player_name=request.player_name
    )
    if not game:
        raise HTTPException(status_code=400, detail="Cannot join game")
    return game.to_dict()

@app.post("/games/{game_id}/resign")
async def resign_game(game_id: str, player_id: str):
    game = GameService.resign_game(game_id, player_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found or you are not a player")
    return game.to_dict()

@app.post("/games/{game_id}/move/{board_index}/{position}")
async def make_move(game_id: str, board_index: int, position: int, player_id: str):
    game, error = GameService.make_move(game_id, board_index, position, player_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

@app.post("/games/{game_id}/start")
async def start_game(game_id: str, player_id: str):
    game = GameService.start_game(game_id, player_id)
    if not game:
        raise HTTPException(status_code=400, detail="Cannot start game")
    return game.to_dict()

@app.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: str):
    """Get player information including name and stats."""
    try:
        player = PlayerService.get_or_create_player(player_id, None)
        if not player:
            logger.error(f"Player not found with ID: {player_id}")
            raise HTTPException(status_code=404, detail=f"Player not found with ID: {player_id}")
        # Return the player directly and let FastAPI handle the conversion
        return player
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Player not found: {str(e)}")

@app.post("/players/{player_id}/name")
async def update_player_name(player_id: str, request: PlayerNameUpdate):
    success = PlayerService.update_player_name(player_id, request.name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update player name")
    return {"success": True} 