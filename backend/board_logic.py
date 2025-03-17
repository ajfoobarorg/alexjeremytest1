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

class MetaBoard:
    """
    Represents the meta-board in Ultimate Tic-Tac-Toe, tracking the state of the 9 larger boards.
    Each position can be empty (""), won by a player ("X"/"O"), or tied ("T").
    This is a read-only view computed from the actual board states.
    """
    
    def __init__(self, boards: List[Board]):
        """
        Initialize a meta-board from a list of Board objects.
        
        Args:
            boards: List of 9 Board objects representing the game state
        """
        if len(boards) != 9:
            raise ValueError("MetaBoard must have exactly 9 boards")
            
        # Compute the state from the boards
        self._state = ["" for _ in range(9)]
        for i, board in enumerate(boards):
            winner = board.check_winner()
            if winner:
                self._state[i] = winner
            elif board.is_full():
                self._state[i] = "T"
    
    def get_winner(self) -> Optional[str]:
        """Return 'X', 'O' if there's a winner, None otherwise."""
        return Board.check_winner_from_list(self._state)
    
    def is_full(self) -> bool:
        """Check if meta-board is full (no empty spaces)."""
        return "" not in self._state
    
    def is_board_playable(self, board_index: int) -> bool:
        """
        Check if a specific board can be played in.
        
        Args:
            board_index: Index of board to check (0-8)
        Returns:
            bool: True if board is empty (not won/tied)
        """
        if not 0 <= board_index <= 8:
            raise ValueError("Board index must be between 0 and 8")
        return self._state[board_index] == ""
    
    def to_list(self) -> List[str]:
        """Return list representation for API responses."""
        return self._state.copy()
    
    def to_json(self) -> str:
        """Return JSON string representation for database storage."""
        return json.dumps(self._state)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"MetaBoard({self._state})"