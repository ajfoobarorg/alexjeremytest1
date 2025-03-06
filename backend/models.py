import datetime
import json
from peewee import *
from db_config import DB_PATH

# Initialize database
db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class Game(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    current_player = CharField(default="X")
    next_board = IntegerField(null=True)
    winner = CharField(null=True)
    game_over = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    is_public = BooleanField(default=False)
    player_x = CharField(null=True)
    player_o = CharField(null=True)
    player_x_name = CharField(null=True)
    player_o_name = CharField(null=True)
    
    # JSON fields
    meta_board = TextField(default=json.dumps(["" for _ in range(9)]))
    boards = TextField(default=json.dumps([[""]*9 for _ in range(9)]))
    
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
            'created_at': self.created_at.isoformat(),
            'is_public': self.is_public,
            'player_x': self.player_x,
            'player_o': self.player_o,
            'player_x_name': self.player_x_name,
            'player_o_name': self.player_o_name
        }

class GameStats(BaseModel):
    id = AutoField()
    total_games = IntegerField(default=0)
    completed_games = IntegerField(default=0)
    x_wins = IntegerField(default=0)
    o_wins = IntegerField(default=0)
    draws = IntegerField(default=0)
    ongoing_games = IntegerField(default=0)
    
    def to_dict(self):
        return {
            'total_games': self.total_games,
            'completed_games': self.completed_games,
            'x_wins': self.x_wins,
            'o_wins': self.o_wins,
            'draws': self.draws,
            'ongoing_games': self.ongoing_games
        }

def initialize_db():
    """Create tables and initialize stats if needed."""
    db.connect()
    db.create_tables([Game, GameStats])
    
    # Create default stats record if it doesn't exist
    if GameStats.select().count() == 0:
        GameStats.create()
    
    db.close() 