from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

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
    board: List[str]
    current_player: str
    winner: Optional[str] = None
    game_over: bool = False

# Initialize empty game state
game_state = GameState(
    board=["" for _ in range(9)],
    current_player="X"
)

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

@app.get("/game")
async def get_game_state():
    return game_state

@app.post("/move/{position}")
async def make_move(position: int):
    if not 0 <= position <= 8:
        raise HTTPException(status_code=400, detail="Invalid position")
    
    if game_state.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    if game_state.board[position]:
        raise HTTPException(status_code=400, detail="Position already taken")
    
    # Make the move
    game_state.board[position] = game_state.current_player
    
    # Check for winner
    winner = check_winner(game_state.board)
    if winner:
        game_state.winner = winner
        game_state.game_over = True
    # Check for draw
    elif "" not in game_state.board:
        game_state.game_over = True
    else:
        # Switch player
        game_state.current_player = "O" if game_state.current_player == "X" else "X"
    
    return game_state

@app.post("/reset")
async def reset_game():
    global game_state
    game_state = GameState(
        board=["" for _ in range(9)],
        current_player="X"
    )
    return game_state 