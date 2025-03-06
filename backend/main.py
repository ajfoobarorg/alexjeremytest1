from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from config import config
import sys
import logging
from models import Game as GameModel, GameStats as GameStatsModel, initialize_db
from board_logic import Board, GameLogic
import json

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

class Square(str, Enum):
    """Represents a single square on a tic-tac-toe board."""
    EMPTY = ""
    X = "X"
    O = "O"

class Board:
    """Internal representation of a tic-tac-toe board."""
    def __init__(self):
        self._squares = ["" for _ in range(9)]
    
    def get(self, pos: int) -> str:
        """Get the value of a square at position 0-8."""
        if not 0 <= pos <= 8:
            raise ValueError("Position must be between 0 and 8")
        return self._squares[pos]
    
    def set(self, pos: int, value: str) -> None:
        """Set a square to a value."""
        if not 0 <= pos <= 8:
            raise ValueError("Position must be between 0 and 8")
        if value not in ["", "X", "O"]:
            raise ValueError("Value must be '', 'X', or 'O'")
        self._squares[pos] = value
    
    def to_list(self) -> List[str]:
        """Convert board to list of strings for API responses."""
        result = self._squares.copy()
        # Ensure all elements are strings
        for i in range(len(result)):
            if result[i] is None:
                result[i] = ""
        return result
    
    def is_full(self) -> bool:
        """Check if board has no empty squares."""
        return "" not in self._squares
    
    def check_winner(self) -> Optional[str]:
        """Check if this board has a winner."""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        
        for line in lines:
            if (self._squares[line[0]] and 
                self._squares[line[0]] == self._squares[line[1]] == self._squares[line[2]]):
                return self._squares[line[0]]
        return None

class GameState(BaseModel):
    id: str
    name: str
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
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Always initialize boards
        self._boards = [Board() for _ in range(9)]
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """Override dict method to include boards in API response."""
        result = super().dict(*args, **kwargs)
        # Convert _boards to list of lists for API
        result["boards"] = [board.to_list() for board in self._boards]
        # Remove private field from response
        if "_boards" in result:
            del result["_boards"]
        return result
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """Override model_dump method for newer Pydantic versions."""
        result = super().model_dump(*args, **kwargs) if hasattr(super(), "model_dump") else super().dict(*args, **kwargs)
        # Convert _boards to list of lists for API
        result["boards"] = [board.to_list() for board in self._boards]
        # Remove private field from response
        if "_boards" in result:
            del result["_boards"]
        return result
    
    def get_board(self, index: int) -> Board:
        """Get a board object by index."""
        if not 0 <= index <= 8:
            raise ValueError("Board index must be between 0 and 8")
        return self._boards[index]

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

# Initialize database
initialize_db()

def is_board_playable(meta_board: List[str], board_index: int, board: Board) -> bool:
    """Check if a board can be played in."""
    return meta_board[board_index] == "" and not board.is_full()

@app.post("/games/new")
async def create_game(request: NewGameRequest):
    game_id = str(uuid.uuid4())
    
    # Create new game in database
    game = GameModel.create(
        id=game_id,
        name=request.game_name,
        current_player="X",
        next_board=None,
        created_at=datetime.now(),
        is_public=request.is_public,
        player_x=request.player_id,
        player_x_name=request.player_name
    )
    
    # Update stats
    stats = GameStatsModel.get()
    stats.total_games += 1
    stats.ongoing_games += 1
    stats.save()
    
    return game.to_dict()

@app.get("/games/public")
async def get_public_games():
    query = GameModel.select().where(
        (GameModel.is_public == True) & 
        (GameModel.game_over == False) & 
        (GameModel.player_o.is_null())
    )
    return [game.to_dict() for game in query]

@app.get("/")
def read_root():
    return {"Hello World": "Quick test. Oh and python version is " + sys.version}

@app.get("/games/{game_id}")
async def get_game(game_id: str):
    try:
        game = GameModel.get(GameModel.id == game_id)
        return game.to_dict()
    except GameModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Game not found")

@app.post("/games/{game_id}/join")
async def join_game(game_id: str, request: JoinGameRequest):
    try:
        game = GameModel.get(GameModel.id == game_id)
        
        if game.game_over:
            raise HTTPException(status_code=400, detail="Game is already over")
        
        if game.player_o:
            raise HTTPException(status_code=400, detail="Game is full")
        
        if game.player_x == request.player_id:
            raise HTTPException(status_code=400, detail="You can't play against yourself")
        
        game.player_o = request.player_id
        game.player_o_name = request.player_name
        game.save()
        
        return game.to_dict()
    except GameModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Game not found")

@app.post("/games/{game_id}/move/{board_index}/{position}")
async def make_move(game_id: str, board_index: int, position: int, player_id: str):
    try:
        game = GameModel.get(GameModel.id == game_id)
        
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
        
        # Get boards from JSON
        boards = GameLogic.get_boards_from_json(game.boards)
        meta_board = json.loads(game.meta_board)
        board = boards[board_index]
        
        # Verify the chosen board is playable
        if not GameLogic.is_board_playable(meta_board, board_index, board):
            raise HTTPException(status_code=400, detail="This board is already completed")
        
        # Verify the position is empty
        if board.get(position):
            raise HTTPException(status_code=400, detail="Position already taken")
        
        # Make the move
        board.set(position, game.current_player)
        
        # Update boards in game model
        game.boards = GameLogic.boards_to_json(boards)
        
        # Check if the small board was won
        small_winner = board.check_winner()
        if small_winner:
            meta_board[board_index] = small_winner
        elif board.is_full():
            meta_board[board_index] = "T"  # T for Tie
        
        # Update meta_board in game model
        game.meta_board = json.dumps(meta_board)
        
        # Check if the game was won
        winner = GameLogic.check_meta_winner(meta_board)
        
        stats = GameStatsModel.get()
        
        if winner:
            game.winner = winner
            game.game_over = True
            stats.completed_games += 1
            stats.ongoing_games -= 1
            if winner == "X":
                stats.x_wins += 1
            else:
                stats.o_wins += 1
            stats.save()
        # Check for draw in the meta board
        elif "" not in [cell for cell in meta_board if cell != "T"]:
            game.game_over = True
            stats.completed_games += 1
            stats.ongoing_games -= 1
            stats.draws += 1
            stats.save()
        else:
            # Set next board based on the position played
            # If the target board is completed, player can choose any incomplete board
            next_board = boards[position]
            if meta_board[position] != "" or next_board.is_full():
                game.next_board = None
            else:
                game.next_board = position
            
            # Switch player
            game.current_player = "O" if game.current_player == "X" else "X"
        
        game.save()
        return game.to_dict()
        
    except GameModel.DoesNotExist:
        raise HTTPException(status_code=404, detail="Game not found")

@app.get("/stats")
async def get_stats():
    stats = GameStatsModel.get()
    return stats.to_dict() 