import datetime
import json
import shortuuid
from peewee import *
from db_config import DB_PATH
from backend.board_logic import MetaBoard, Board
from typing import List
import sqlite3

# Initialize database with datetime adapter
db = SqliteDatabase(DB_PATH, pragmas={
    'foreign_keys': 1,  # Enable foreign key support
    'journal_mode': 'wal'  # Write-Ahead Logging for better concurrency
}, detect_types=sqlite3.PARSE_DECLTYPES)  # Enable datetime type detection

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    """Player model representing a user of the game."""
    id = CharField(max_length=22, primary_key=True)  # shortuuid is always 22 chars
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=255, unique=True)
    first_name = CharField(max_length=50, null=True)
    last_name = CharField(max_length=50, null=True)
    wins = IntegerField(default=0)
    losses = IntegerField(default=0)
    draws = IntegerField(default=0)
    elo = IntegerField(default=100)
    location = CharField(max_length=100, null=True)
    country = CharField(max_length=2, null=True)  # ISO 3166-1 alpha-2
    timezone = CharField(max_length=50, null=True)  # IANA timezone name or UTC±HH:MM
    created_at = DateTimeField(default=datetime.datetime.now)
    last_active = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
        """Override save to ensure ID is set for new players."""
        if not self.id:
            self.id = shortuuid.uuid()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        """Convert model to dictionary for API response."""
        return {
            'id': self.id,  
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'location': self.location,
            'country': self.country,
            'timezone': self.timezone,
            'stats': {
                'wins': self.wins,
                'losses': self.losses,
                'draws': self.draws,
                'elo': self.elo
            }
        }

class Game(BaseModel):
    """Game model representing a single game of Ultimate Tic-Tac-Toe."""
    id = CharField(max_length=22, primary_key=True)  # shortuuid is always 22 chars
    current_player = CharField(default="X")
    next_board = IntegerField(null=True)
    winner = CharField(null=True)
    game_over = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    completed_at = DateTimeField(null=True)
    
    # Player references with foreign keys
    player_x = ForeignKeyField(Player, backref='games_as_x', null=True)
    player_o = ForeignKeyField(Player, backref='games_as_o', null=True)
    
    # Timing fields
    last_move_time = DateTimeField(default=datetime.datetime.now)
    player_x_time_used = IntegerField(default=0)  # Time used in seconds
    player_o_time_used = IntegerField(default=0)  # Time used in seconds
    TOTAL_TIME_ALLOWED = 360  # 6 minutes in seconds
    
    # ELO tracking
    player_x_elo_change = IntegerField(null=True)  # ELO change for player X
    player_o_elo_change = IntegerField(null=True)  # ELO change for player O
    
    # JSON fields - meta_board is now computed dynamically from boards
    boards = TextField(default=json.dumps([[""]*9 for _ in range(9)]))

    def save(self, *args, **kwargs):
        """Override save to ensure ID is set for new games."""
        if not self.id:
            self.id = shortuuid.uuid()
        return super().save(*args, **kwargs)

    def get_time_remaining(self, player):
        """Get remaining time for a player in seconds."""
        time_used = self.player_x_time_used if player == 'X' else self.player_o_time_used
        return max(0, self.TOTAL_TIME_ALLOWED - time_used)
    
    def update_time_used(self):
        """Update time used by current player based on last move time."""
        now = datetime.datetime.now()
        elapsed = int((now - self.last_move_time).total_seconds())
        
        if self.current_player == 'X':
            self.player_x_time_used += elapsed
        else:
            self.player_o_time_used += elapsed
            
        self.last_move_time = now
        self.save()  # Save the updated time
        return self.get_time_remaining(self.current_player)
    
    def get_boards(self) -> List[Board]:
        """Get the list of Board objects."""
        boards_data = json.loads(self.boards)
        return [Board(squares) for squares in boards_data]
    
    def set_boards(self, boards: List[Board]) -> None:
        """Save the list of Board objects."""
        self.boards = json.dumps([board.to_list() for board in boards])
    
    def get_meta_board(self) -> MetaBoard:
        """Get the current meta board state."""
        return MetaBoard(self.get_boards())
    
    def to_dict(self):
        """Convert model to dictionary for API response."""
        meta = self.get_meta_board()
        boards = self.get_boards()
        
        # Get player ELO ratings if available
        player_x_elo = self.player_x.elo if self.player_x else None
        player_o_elo = self.player_o.elo if self.player_o else None
        
        return {
            'id': self.id,
            'meta_board': meta.to_list(),
            'boards': [board.to_list() for board in boards],
            'current_player': self.current_player,
            'next_board': self.next_board,
            'winner': self.winner,
            'game_over': self.game_over,
            'player_x': {
                'id': self.player_x.id if self.player_x else None,  
                'username': self.player_x.username if self.player_x else None,
                'time_remaining': self.get_time_remaining('X'),
                'elo': player_x_elo,
                'elo_change': self.player_x_elo_change
            },
            'player_o': {
                'id': self.player_o.id if self.player_o else None,  
                'username': self.player_o.username if self.player_o else None,
                'time_remaining': self.get_time_remaining('O'),
                'elo': player_o_elo,
                'elo_change': self.player_o_elo_change
            }
        }

def initialize_db():
    """Create tables if they don't exist."""
    db.connect()
    db.create_tables([Player, Game])
    db.close() 