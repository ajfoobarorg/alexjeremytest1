import datetime
import json
from peewee import *
from db_config import DB_PATH

# Initialize database
db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    """Player model representing a user of the game."""
    id = CharField(primary_key=True)
    name = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    
    # Player statistics
    wins = IntegerField(default=0)
    losses = IntegerField(default=0)
    draws = IntegerField(default=0)

class Game(BaseModel):
    """Game model representing a single game of Ultimate Tic-Tac-Toe."""
    id = CharField(primary_key=True)
    name = CharField()
    current_player = CharField(default="X")
    next_board = IntegerField(null=True)
    winner = CharField(null=True)
    game_over = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    is_public = BooleanField(default=False)
    game_started = BooleanField(default=False)
    
    # Player references with foreign keys
    player_x = ForeignKeyField(Player, backref='games_as_x', null=True)
    player_o = ForeignKeyField(Player, backref='games_as_o', null=True)
    
    # We keep player names in the Game model for convenience
    player_x_name = CharField(null=True)
    player_o_name = CharField(null=True)
    
    # Timing fields
    last_move_time = DateTimeField(default=datetime.datetime.now)
    player_x_time_used = IntegerField(default=0)  # Time used in seconds
    player_o_time_used = IntegerField(default=0)  # Time used in seconds
    TOTAL_TIME_ALLOWED = 360  # 6 minutes in seconds
    
    # JSON fields
    meta_board = TextField(default=json.dumps(["" for _ in range(9)]))
    boards = TextField(default=json.dumps([[""]*9 for _ in range(9)]))
    
    def get_time_remaining(self, player):
        """Get remaining time for a player in seconds."""
        if not self.game_started:
            return self.TOTAL_TIME_ALLOWED
            
        time_used = self.player_x_time_used if player == 'X' else self.player_o_time_used
        return max(0, self.TOTAL_TIME_ALLOWED - time_used)
    
    def update_time_used(self):
        """Update time used by current player based on last move time."""
        if not self.game_started:
            return self.TOTAL_TIME_ALLOWED
            
        now = datetime.datetime.now()
        elapsed = int((now - self.last_move_time).total_seconds())
        
        if self.current_player == 'X':
            self.player_x_time_used += elapsed
        else:
            self.player_o_time_used += elapsed
            
        self.last_move_time = now
        return self.get_time_remaining(self.current_player)
    
    # Since we have special logic here for the boards, we must override the default to_dict method
    def to_dict(self):
        """Convert model to dictionary for API response."""
        return {
            'id': self.id,
            'name': self.name,
            'meta_board': json.loads(self.meta_board),
            'boards': json.loads(self.boards),
            'current_player': self.current_player,
            'next_board': self.next_board,
            'winner': self.winner,
            'game_over': self.game_over,
            'is_public': self.is_public,
            'player_x': {
                'id': self.player_x.id if self.player_x else None,
                'name': self.player_x_name,
                'time_remaining': self.get_time_remaining('X')
            },
            'player_o': {
                'id': self.player_o.id if self.player_o else None,
                'name': self.player_o_name,
                'time_remaining': self.get_time_remaining('O')
            },
            'game_started': self.game_started
        }

def initialize_db():
    """Create tables if they don't exist."""
    db.connect()
    db.create_tables([Player, Game])
    db.close() 