from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState(BaseModel):
    id: str
    name: str
    boards: List[List[str]]  # 9 separate boards, each with 9 positions
    meta_board: List[str]    # The big board showing which small boards are won
    current_player: str
    next_board: Optional[int] = None  # Which board (0-8) must be played in next, None if player can choose
    winner: Optional[str] = None
    game_over: bool = False
    created_at: datetime
    is_public: bool
    player_x: Optional[str] = None  # Player ID for X
    player_o: Optional[str] = None  # Player ID for O
    player_x_name: Optional[str] = None  # Player name for X
    player_o_name: Optional[str] = None  # Player name for O

class GameStats(BaseModel):
    total_games: int = 0
    completed_games: int = 0
    x_wins: int = 0
    o_wins: int = 0
    draws: int = 0
    ongoing_games: int = 0

class NewGameRequest(BaseModel):
    is_public: bool
    player_id: str
    player_name: str
    game_name: str

class JoinGameRequest(BaseModel):
    player_id: str
    player_name: str

# Store games in memory (in production, use a database)
games: Dict[str, GameState] = {}
stats = GameStats()

def check_winner(board: List[str]) -> Optional[str]:
    # Winning combinations
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]  # Diagonals
    ]
    
    for line in lines:
        if board[line[0]] and board[line[0]] == board[line[1]] == board[line[2]]:
            return board[line[0]]
    return None

def is_board_full(board: List[str]) -> bool:
    return "" not in board

def is_board_playable(meta_board: List[str], board_index: int) -> bool:
    return meta_board[board_index] == "" and not is_board_full(board_index)

@app.post("/games/new")
async def create_game(request: NewGameRequest):
    game_id = str(uuid.uuid4())
    new_game = GameState(
        id=game_id,
        name=request.game_name,
        boards=[["" for _ in range(9)] for _ in range(9)],  # 9 empty boards
        meta_board=["" for _ in range(9)],  # Empty big board
        current_player="X",
        next_board=None,  # First player can play in any board
        created_at=datetime.now(),
        is_public=request.is_public,
        player_x=request.player_id,
        player_x_name=request.player_name
    )
    games[game_id] = new_game
    stats.total_games += 1
    stats.ongoing_games += 1
    return new_game

@app.get("/games/public")
async def get_public_games():
    public_games = [game for game in games.values() 
                   if game.is_public and not game.game_over and game.player_o is None]
    return public_games

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/games/{game_id}")
async def get_game(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id]

@app.post("/games/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if game.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    if game.player_o:
        raise HTTPException(status_code=400, detail="Game is full")
    
    if game.player_x == request.player_id:
        raise HTTPException(status_code=400, detail="You can't play against yourself")
    
    game.player_o = request.player_id
    game.player_o_name = request.player_name
    return game

@app.post("/games/{game_id}/move/{board_index}/{position}")
async def make_move(game_id: str, board_index: int, position: int, player_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if not (0 <= board_index <= 8 and 0 <= position <= 8):
        raise HTTPException(status_code=400, detail="Invalid position")
    
    if game.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    # Verify it's the player's turn
    current_player_id = game.player_x if game.current_player == "X" else game.player_o
    if current_player_id != player_id:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    # Verify the move is in the correct board
    if game.next_board is not None and game.next_board != board_index:
        raise HTTPException(status_code=400, detail="Must play in the indicated board")
    
    # Verify the chosen board is playable
    if game.meta_board[board_index] != "" or is_board_full(game.boards[board_index]):
        raise HTTPException(status_code=400, detail="This board is already completed")
    
    # Verify the position is empty
    if game.boards[board_index][position]:
        raise HTTPException(status_code=400, detail="Position already taken")
    
    # Make the move
    game.boards[board_index][position] = game.current_player
    
    # Check if the small board was won
    small_winner = check_winner(game.boards[board_index])
    if small_winner:
        game.meta_board[board_index] = small_winner
    elif is_board_full(game.boards[board_index]):
        game.meta_board[board_index] = "T"  # T for Tie
    
    # Check if the game was won
    winner = check_winner(game.meta_board)
    if winner:
        game.winner = winner
        game.game_over = True
        stats.completed_games += 1
        stats.ongoing_games -= 1
        if winner == "X":
            stats.x_wins += 1
        else:
            stats.o_wins += 1
    # Check for draw in the meta board
    elif "" not in [cell for cell in game.meta_board if cell != "T"]:
        game.game_over = True
        stats.completed_games += 1
        stats.ongoing_games -= 1
        stats.draws += 1
    else:
        # Set next board based on the position played
        # If the target board is completed, player can choose any incomplete board
        if game.meta_board[position] != "" or is_board_full(game.boards[position]):
            game.next_board = None
        else:
            game.next_board = position
        
        # Switch player
        game.current_player = "O" if game.current_player == "X" else "X"
    
    return game

@app.get("/stats")
async def get_stats():
    return stats 