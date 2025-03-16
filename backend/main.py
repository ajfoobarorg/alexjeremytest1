from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import datetime
from datetime import timedelta

from config import config
from models import initialize_db, Player, Game
from schemas import (
    MatchmakingRequest, MatchmakingResponse, GameResponse,
    SignupRequest, LoginRequest, ProfileUpdateRequest, StatsResponse
)
from services import GameService, ProfileService
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

def set_player_id_cookie(response: Response, player_id: str) -> None:
    """Helper function to set the player ID cookie consistently."""
    # Blank comment -- TODO(aroetter): delete
    response.set_cookie(
        key="playerId",
        value=player_id,
        max_age=365 * 24 * 60 * 60,  # 1 year
        httponly=True,
        samesite="lax",  # Allow cross-site requests while maintaining security
        secure=config.IS_PRODUCTION,  # Only set secure in production
        path="/",
        domain=config.BACKEND_DOMAIN  # Set to backend domain explicitly
    )

# Auth endpoints
@app.post("/auth/signup")
def signup(request: SignupRequest, response: Response) -> dict:
    # Check if username or email already exists
    if ProfileService.check_username_exists(request.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if ProfileService.check_email_exists(request.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create new player profile
    player = ProfileService.create_profile(
        username=request.username,
        email=request.email,
        level=request.level,
        timezone=request.timezone,
        country=request.country
    )
    
    # Set cookie with player ID
    set_player_id_cookie(response, player.id)
    return {"id": player.id}

@app.post("/auth/login")
def login(request: Request, request_data: LoginRequest, response: Response):
    player = ProfileService.get_profile_by_email(request_data.email)
    if not player:
        raise HTTPException(status_code=404, detail="Email not found")
    
    set_player_id_cookie(response, player.id)
    return {"player_id": player.id}

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(
        key="playerId",
        httponly=True,
        samesite="lax",
        path="/",
        secure=config.IS_PRODUCTION,
        domain=config.BACKEND_DOMAIN
    )
    return {"message": "Logged out successfully"}

@app.get("/profile/me")
def get_current_profile(request: Request):
    player_id = request.cookies.get("playerId")
    if not player_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    player = ProfileService.get_profile(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return player.to_dict()

@app.get("/profile/{player_id}")
def get_profile(player_id: str):
    player = ProfileService.get_profile(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player.to_dict()

@app.post("/profile/{player_id}")
def update_profile(player_id: str, request: ProfileUpdateRequest):
    # Check if email/username changes would conflict with existing users
    if request.email:
        existing_email = ProfileService.check_email_exists(request.email)
        if existing_email and request.email != ProfileService.get_profile(player_id).email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    if request.username:
        existing_username = ProfileService.check_username_exists(request.username)
        if existing_username and request.username != ProfileService.get_profile(player_id).username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Update profile with provided data
    player = ProfileService.update_profile(
        player_id,
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        location=request.location,
        country=request.country,
        timezone=request.timezone
    )
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return player.to_dict()

# Stats endpoint
@app.get("/stats")
def get_stats() -> StatsResponse:
    # Get timestamps for our time windows
    now = datetime.datetime.utcnow()
    last_24h = now - timedelta(days=1)
    last_7d = now - timedelta(days=7)
    
    # Count games played in last 24 hours
    games_today = Game.select().where(
        Game.created_at >= last_24h
    ).count()
    
    # Count unique players who played in last 7 days
    active_players = (Player
        .select()
        .join(Game, on=((Player.id == Game.player_x) | (Player.id == Game.player_o)))
        .where(Game.created_at >= last_7d)
        .group_by(Player.id)
        .count())
    
    return StatsResponse(
        games_today=games_today,
        players_online=active_players
    )

@app.get("/")
def read_root():
    return {"message": "Ultimate Tic-Tac-Toe API"}

@app.get("/games/{game_id}")
def get_game(game_id: str):
    game = GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

# Matchmaking endpoints
@app.post("/matchmaking/join")
def join_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Join the matchmaking queue"""
    if not MatchmakingService.add_player(request.player_id):
        raise HTTPException(status_code=400, detail="Could not add player to matchmaking")
    return MatchmakingResponse(status="waiting")

@app.post("/matchmaking/ping")
def ping_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Ping to check matchmaking status and keep player in queue"""
    # Update player's presence
    MatchmakingService.update_ping(request.player_id)
    
    # Check for match
    game, error, opponent_name, match_accepted = MatchmakingService.find_match(request.player_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    if game and match_accepted:
        # Both players have accepted, return game ID
        return MatchmakingResponse(
            status="matched",
            game_id=str(game.id),
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
def cancel_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Cancel matchmaking for a player"""
    if MatchmakingService.remove_player(request.player_id):
        return MatchmakingResponse(status="cancelled")
    raise HTTPException(status_code=400, detail="Player not in matchmaking")

# Game action endpoints
@app.post("/games/{game_id}/move/{board_index}/{position}")
def make_move(game_id: str, board_index: int, position: int, player_id: str):
    game, error = GameService.make_move(game_id, board_index, position, player_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

@app.post("/games/{game_id}/resign")
def resign_game(game_id: str, player_id: str):
    game = GameService.resign_game(game_id, player_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()

@app.post("/games/{game_id}/ready")
def ready_game(game_id: str, player_id: str) -> GameResponse:
    """Signal that player X is ready to start the game"""
    game = GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Only player X can signal ready
    if game.player_x.id != player_id:
        logging.error(f"Only player X can signal ready: {game.player_x.id} != {player_id}")
        raise HTTPException(status_code=400, detail="Only player X can signal ready")
    
    # Start the game by setting the initial last_move_time
    game.last_move_time = datetime.datetime.now()
    game.save()
    
    return GameResponse(**game.to_dict()) 