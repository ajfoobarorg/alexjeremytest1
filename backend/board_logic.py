import json

class Board:
    """Board logic for a single tic-tac-toe board."""
    
    def __init__(self, squares=None):
        self._squares = squares if squares else ["" for _ in range(9)]
    
    def get(self, pos):
        """Get the value at position."""
        if not 0 <= pos <= 8:
            raise ValueError("Position must be between 0 and 8")
        return self._squares[pos]
    
    def set(self, pos, value):
        """Set a value at position."""
        if not 0 <= pos <= 8:
            raise ValueError("Position must be between 0 and 8")
        if value not in ["", "X", "O"]:
            raise ValueError("Value must be '', 'X', or 'O'")
        self._squares[pos] = value
    
    def to_list(self):
        """Convert to list representation."""
        return self._squares.copy()
    
    def is_full(self):
        """Check if board is full."""
        return "" not in self._squares
    
    def check_winner(self):
        """Check if there's a winner."""
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

class GameLogic:
    """Game logic for Ultimate Tic-Tac-Toe."""
    
    @staticmethod
    def get_boards_from_json(boards_json):
        """Convert JSON boards to Board objects."""
        boards_data = json.loads(boards_json)
        return [Board(board) for board in boards_data]
    
    @staticmethod
    def boards_to_json(boards):
        """Convert Board objects to JSON."""
        return json.dumps([board.to_list() for board in boards])
    
    @staticmethod
    def is_board_playable(meta_board, board_index, board):
        """Check if a board can be played in."""
        meta_board_list = json.loads(meta_board) if isinstance(meta_board, str) else meta_board
        return meta_board_list[board_index] == "" and not board.is_full()
    
    @staticmethod
    def check_meta_winner(meta_board):
        """Check if there's a winner in the meta board."""
        meta_board_list = json.loads(meta_board) if isinstance(meta_board, str) else meta_board
        
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        
        for line in lines:
            if (meta_board_list[line[0]] and meta_board_list[line[0]] != "T" and
                meta_board_list[line[0]] == meta_board_list[line[1]] == meta_board_list[line[2]]):
                return meta_board_list[line[0]]
        return None 