from pydantic import BaseModel, ConfigDict, EmailStr, validator
from typing import List, Optional
from enum import Enum
import zoneinfo
import pycountry

# Use IANA timezone names from zoneinfo
VALID_TIMEZONES = set(zoneinfo.available_timezones())

class PlayerLevel(str, Enum):
    NEW = "0"
    BEGINNER = "1"
    INTERMEDIATE = "2"
    ADVANCED = "3"

# Auth request models
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    level: PlayerLevel
    timezone: Optional[str] = None
    country: Optional[str] = None

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None and v not in VALID_TIMEZONES:
            raise ValueError('Invalid timezone. Must be a valid IANA timezone name.')
        return v

    @validator('country')
    def validate_country(cls, v):
        if v is not None:
            country = pycountry.countries.get(alpha_2=v.upper())
            if not country:
                raise ValueError('Invalid country code. Must be a valid ISO 3166-1 alpha-2 code.')
        return v.upper() if v else v

class LoginRequest(BaseModel):
    email: EmailStr

class ProfileUpdateRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    location: str | None = None
    country: str | None = None
    timezone: str | None = None

    @validator('country')
    def validate_country(cls, v):
        if v is not None:
            country = pycountry.countries.get(alpha_2=v.upper())
            if not country:
                raise ValueError('Invalid country code. Must be a valid ISO 3166-1 alpha-2 code.')
        return v.upper() if v else v

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None and v not in VALID_TIMEZONES:
            raise ValueError('Invalid timezone. Must be a valid IANA timezone name.')
        return v

class GamePlayerInfo(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    time_remaining: int = 360  # Default to 6 minutes in seconds
    elo: Optional[int] = None
    elo_change: Optional[int] = None

class GameResponse(BaseModel):
    id: str
    meta_board: List[str]  # Computed dynamically from boards state
    boards: List[List[str]]
    current_player: str
    next_board: Optional[int]
    winner: Optional[str]
    game_over: bool
    player_x: GamePlayerInfo
    player_o: GamePlayerInfo
    
    model_config = ConfigDict(from_attributes=True)

# Stats schemas
class StatsResponse(BaseModel):
    games_today: int
    players_online: int

# Matchmaking schemas
class MatchmakingRequest(BaseModel):
    player_id: str

class MatchmakingResponse(BaseModel):
    """Response for matchmaking operations"""
    status: str  # "waiting", "waiting_acceptance", "matched", "cancelled", "error"
    game_id: Optional[str] = None
    opponent_name: Optional[str] = None
    message: Optional[str] = None