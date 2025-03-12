import logging
import json
from typing import List, Optional, Union

class Board:
    """Board logic for a single tic-tac-toe board."""
    
    def __init__(self, squares: List[str] = None):
        self._squares = squares if squares else ["" for _ in range(9)]
    
    def get(self, pos: int) -> str:
        """Get the value at position."""
        if not 0 <= pos <= 8:
            raise ValueError("Position must be between 0 and 8")
        return self._squares[pos]
    
    def set(self, pos: int, value: str) -> None:
        """Set a value at position."""
        if not 0 <= pos <= 8:
            raise ValueError("Position must be between 0 and 8")
        if value not in ["", "X", "O"]:
            raise ValueError("Value must be '', 'X', or 'O'")
        self._squares[pos] = value
    
    def to_list(self) -> List[str]:
        """Convert to list representation."""
        return self._squares.copy()
    
    def is_full(self) -> bool:
        """Check if board is full."""
        return "" not in self._squares
    
    def check_winner(self) -> Optional[str]:
        """Check if there's a winner."""
        return Board.check_winner_from_list(self._squares)
    
    @staticmethod
    def check_winner_from_list(board_as_list: List[str]) -> Optional[str]:
        """Check if there's a winner from a list representation of a board."""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        
        for line in lines:
            if (board_as_list[line[0]] and board_as_list[line[0]] != "T" and
                board_as_list[line[0]] == board_as_list[line[1]] == board_as_list[line[2]]):
                return board_as_list[line[0]]
        return None

class GameLogic:
    """Game logic for Ultimate Tic-Tac-Toe."""
    
    @staticmethod
    def get_boards_from_json(boards_json: str) -> List[Board]:
        """Convert JSON boards to Board objects."""
        boards_data = json.loads(boards_json)
        return [Board(board) for board in boards_data]
    
    @staticmethod
    def boards_to_json(boards: List[Board]) -> str:
        """Convert Board objects to JSON."""
        return json.dumps([board.to_list() for board in boards])
    
    @staticmethod
    def is_board_playable(meta_board: Union[str, List[str]], board_index: int, board: Board) -> bool:
        """Check if a board can be played in."""
        # I believe meta_board list is just a list of nine strings, representing who was
        # the winner of each board, or blank if no one has won on that board yet.
        meta_board_list = json.loads(meta_board) if isinstance(meta_board, str) else meta_board
        return meta_board_list[board_index] == "" and not board.is_full()
    
    @staticmethod
    def check_winner(board: Union[List[str], Board]) -> Optional[str]:
        """Check if there's a winner in a board or meta-board."""
        #TODO(aroetter): I don't think the meta-board comment above is correct.
        if isinstance(board, Board):
            logging.fatal("TODO(aroetteR): CHECK TO SEE THIS NEVER HAPPENS. Consider deleting")
            return board.check_winner()
            
        # Handle list representation
        return Board.check_winner_from_list(board)
    
    @staticmethod
    def is_board_full(board: Union[List[str], Board]) -> bool:
        """Check if a board or meta-board is full."""
        if isinstance(board, Board):
            return board.is_full()
            
        # For meta-board, check if all positions are filled (not empty)
        return "" not in board 