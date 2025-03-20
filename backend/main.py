# Standard library imports
import datetime
import logging
from datetime import timedelta

# Third-party imports
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from config import config
from matchmaking import MatchmakingService
from models import Game, Player, initialize_db
from schemas import (
    GameResponse,
    LoginRequest,
    MatchmakingRequest,
    MatchmakingResponse,
    ProfileUpdateRequest,
    SignupRequest,
    StatsResponse,
)
from services import GameService, ProfileService

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
    """Helper function to set the player ID cookie consistently.

    Args:
        response: The FastAPI response object to add the cookie to.
        player_id: The player ID to store in the cookie.
    """
    response.set_cookie(
        key="playerId",
        value=player_id,
        max_age=365 * 24 * 60 * 60,  # 1 year
        httponly=True,
        samesite="none" if config.IS_PRODUCTION else "lax",
        secure=config.IS_PRODUCTION,  # Only set secure in production
        path="/",
        domain=config.BACKEND_DOMAIN,  # Set to backend domain explicitly
    )


# Auth endpoints
@app.post("/auth/signup")
def signup(request: SignupRequest, response: Response) -> dict:
    """Create a new player account.

    Args:
        request: The signup request containing user information.
        response: The response object for setting cookies.

    Returns:
        A dictionary containing the ID of the newly created player.

    Raises:
        HTTPException: If username or email already exists.
    """
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
        country=request.country,
    )

    # Set cookie with player ID
    set_player_id_cookie(response, player.id)
    return {"id": player.id}


@app.post("/auth/login")
def login(request: Request, request_data: LoginRequest, response: Response):
    """Log in an existing player by email.

    Args:
        request: The FastAPI request object.
        request_data: The login request data containing the email.
        response: The response object for setting cookies.

    Returns:
        A dictionary containing the player ID.

    Raises:
        HTTPException: If the email is not found.
    """
    player = ProfileService.get_profile_by_email(request_data.email)
    if not player:
        raise HTTPException(status_code=404, detail="Email not found")

    set_player_id_cookie(response, player.id)
    return {"player_id": player.id}


@app.post("/auth/logout")
def logout(response: Response):
    """Log out the current player by removing their cookie.

    Args:
        response: The response object for deleting cookies.

    Returns:
        A dictionary containing a success message.
    """
    response.delete_cookie(
        key="playerId",
        httponly=True,
        samesite="none" if config.IS_PRODUCTION else "lax",
        path="/",
        secure=config.IS_PRODUCTION,
        domain=config.BACKEND_DOMAIN,
    )
    return {"message": "Logged out successfully"}


@app.get("/profile/me")
def get_current_profile(request: Request):
    """Get the profile of the currently logged-in player.

    Args:
        request: The FastAPI request object containing cookies.

    Returns:
        The player profile as a dictionary.

    Raises:
        HTTPException: If not logged in or player not found.
    """
    player_id = request.cookies.get("playerId")
    if not player_id:
        raise HTTPException(status_code=401, detail="Not logged in")

    player = ProfileService.get_profile(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player.to_dict()


@app.get("/profile/{player_id}")
def get_profile(player_id: str):
    """Get a player's profile by ID.

    Args:
        player_id: The ID of the player to retrieve.

    Returns:
        The player profile as a dictionary.

    Raises:
        HTTPException: If player not found.
    """
    player = ProfileService.get_profile(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player.to_dict()


@app.post("/profile/{player_id}")
def update_profile(player_id: str, request: ProfileUpdateRequest):
    # Check if email/username changes would conflict with existing users
    if request.email:
        existing_email = ProfileService.check_email_exists(request.email)
        if (
            existing_email
            and request.email != ProfileService.get_profile(player_id).email
        ):
            raise HTTPException(status_code=400, detail="Email already registered")

    if request.username:
        existing_username = ProfileService.check_username_exists(request.username)
        if (
            existing_username
            and request.username != ProfileService.get_profile(player_id).username
        ):
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
        timezone=request.timezone,
    )

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    return player.to_dict()


# Stats endpoint
@app.get("/stats")
def get_stats() -> StatsResponse:
    """Get global game statistics.

    Returns:
        A StatsResponse object containing game and player statistics.
    """
    # Get timestamps for our time windows
    now = datetime.datetime.utcnow()
    last_24h = now - timedelta(days=1)
    last_7d = now - timedelta(days=7)

    # Count games played in last 24 hours
    games_today = Game.select().where(Game.created_at >= last_24h).count()

    # Count unique players who played in last 7 days
    active_players = (
        Player.select()
        .join(Game, on=((Player.id == Game.player_x) | (Player.id == Game.player_o)))
        .where(Game.created_at >= last_7d)
        .group_by(Player.id)
        .count()
    )

    return StatsResponse(games_today=games_today, players_online=active_players)


@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message.

    Returns:
        A dictionary containing a welcome message.
    """
    return {"message": "Ultimate Tic-Tac-Toe API"}


@app.get("/games/{game_id}")
def get_game(game_id: str):
    """Get a game by ID.

    Args:
        game_id: The ID of the game to retrieve.

    Returns:
        The game data as a dictionary.

    Raises:
        HTTPException: If game not found.
    """
    game = GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()


# Matchmaking endpoints
@app.post("/matchmaking/join")
def join_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Join the matchmaking queue"""
    if not MatchmakingService.add_player(request.player_id):
        raise HTTPException(
            status_code=400, detail="Could not add player to matchmaking"
        )
    return MatchmakingResponse(status="waiting")


@app.post("/matchmaking/ping")
def ping_matchmaking(request: MatchmakingRequest) -> MatchmakingResponse:
    """Ping to check matchmaking status and keep player in queue"""
    # Update player's presence
    MatchmakingService.update_ping(request.player_id)

    # Check for match
    game, error, opponent_name, match_accepted = MatchmakingService.find_match(
        request.player_id
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    if game and match_accepted:
        # Both players have accepted, return game ID
        return MatchmakingResponse(
            status="matched", game_id=str(game.id), opponent_name=opponent_name
        )
    elif opponent_name:
        # Match found but waiting for acceptance
        return MatchmakingResponse(
            status="waiting_acceptance", opponent_name=opponent_name
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
    """Make a move in a game.

    Args:
        game_id: The ID of the game.
        board_index: The index of the board (0-8).
        position: The position on the board (0-8).
        player_id: The ID of the player making the move.

    Returns:
        The updated game data as a dictionary.

    Raises:
        HTTPException: If the move is invalid or game not found.
    """
    game, error = GameService.make_move(game_id, board_index, position, player_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()


@app.post("/games/{game_id}/resign")
def resign_game(game_id: str, player_id: str):
    """Resign from a game.

    Args:
        game_id: The ID of the game.
        player_id: The ID of the player resigning.

    Returns:
        The updated game data as a dictionary.

    Raises:
        HTTPException: If game not found.
    """
    game = GameService.resign_game(game_id, player_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.to_dict()


@app.post("/games/{game_id}/ready")
def ready_game(game_id: str, player_id: str) -> GameResponse:
    """Signal that player X is ready to start the game.

    Args:
        game_id: The ID of the game.
        player_id: The ID of the player signaling ready.

    Returns:
        The updated game data.

    Raises:
        HTTPException: If game not found or if not player X.
    """
    game = GameService.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Only player X can signal ready
    if game.player_x.id != player_id:
        logging.error(
            f"Only player X can signal ready: {game.player_x.id} != {player_id}"
        )
        raise HTTPException(status_code=400, detail="Only player X can signal ready")

    # Start the game by setting the initial last_move_time
    game.last_move_time = datetime.datetime.now()
    game.started = True
    game.save()

    return GameResponse(**game.to_dict())
