from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Player schemas
class PlayerCreate(BaseModel):
    name: str

class PlayerResponse(BaseModel):
    id: str
    name: str
    wins: int
    losses: int
    draws: int
    
    class Config:
        orm_mode = True

# Game schemas
class GameCreate(BaseModel):
    is_public: bool
    player_id: str
    player_name: str
    game_name: str

class JoinGameRequest(BaseModel):
    player_id: str
    player_name: str

class PlayerNameUpdate(BaseModel):
    name: str

class BoardState(BaseModel):
    cells: List[str]

class GamePlayerInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    time_remaining: int = 360  # Default to 6 minutes in seconds

class GameResponse(BaseModel):
    id: str
    name: str
    meta_board: List[str]
    boards: List[List[str]]
    current_player: str
    next_board: Optional[int]
    winner: Optional[str]
    game_over: bool
    is_public: bool
    player_x: GamePlayerInfo
    player_o: GamePlayerInfo
    game_started: bool
    
    class Config:
        orm_mode = True 