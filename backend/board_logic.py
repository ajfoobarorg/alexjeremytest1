# Standard library imports
from typing import List, Optional

class Board:
    """Represents a single 3x3 tic-tac-toe board."""
    
    def __init__(self, squares: List[str] = None):
        """Initialize a board with optional initial state.
        
        Args:
            squares: List of 9 strings representing the board squares. 
                    Each square can be "X", "O", or "" (empty).
                    If None, creates an empty board.
        """
        self.squares = squares if squares is not None else [""] * 9
        self._winner = None  # Cache winner calculation
    
    def is_full(self) -> bool:
        """Check if the board is full.
        
        Returns:
            True if all squares are filled, False otherwise.
        """
        return all(square != "" for square in self.squares)
    
    def is_empty(self) -> bool:
        """Check if the board is empty.
        
        Returns:
            True if all squares are empty, False otherwise.
        """
        return all(square == "" for square in self.squares)
    
    def get_winner(self) -> Optional[str]:
        """Check if there is a winner on this board.
        
        Returns:
            "X" or "O" if that player has won, "T" for a tie,
            or None if there is no winner yet.
        """
        # Use cached value if available
        if self._winner is not None:
            return self._winner
            
        # Check rows
        for i in range(0, 9, 3):
            if (self.squares[i] != "" and
                self.squares[i] == self.squares[i+1] == self.squares[i+2]):
                self._winner = self.squares[i]
                return self._winner
        
        # Check columns
        for i in range(3):
            if (self.squares[i] != "" and
                self.squares[i] == self.squares[i+3] == self.squares[i+6]):
                self._winner = self.squares[i]
                return self._winner
        
        # Check diagonals
        if (self.squares[0] != "" and
            self.squares[0] == self.squares[4] == self.squares[8]):
            self._winner = self.squares[0]
            return self._winner
            
        if (self.squares[2] != "" and
            self.squares[2] == self.squares[4] == self.squares[6]):
            self._winner = self.squares[2]
            return self._winner
        
        # Check for tie (all squares filled)
        if self.is_full():
            self._winner = "T"
            return self._winner
        
        # No winner yet
        return None
    
    def make_move(self, position: int, player: str) -> bool:
        """Make a move on the board.
        
        Args:
            position: The position to make the move (0-8).
            player: The player making the move ("X" or "O").
            
        Returns:
            True if the move was valid and made, False otherwise.
        """
        # Check if position is valid
        if position < 0 or position > 8:
            return False
            
        # Check if position is empty
        if self.squares[position] != "":
            return False
            
        # Make the move
        self.squares[position] = player
        # Reset winner cache
        self._winner = None
        return True
    
    def to_list(self) -> List[str]:
        """Convert the board to a list representation.
        
        Returns:
            List of 9 strings representing the board squares.
        """
        return self.squares

class MetaBoard:
    """Represents the meta board of an Ultimate Tic-Tac-Toe game."""
    
    def __init__(self, boards: List[Board] = None):
        """Initialize a meta board with optional boards.
        
        Args:
            boards: List of 9 Board objects representing the sub-boards.
                   If None, creates empty boards.
        """
        self.boards = boards if boards is not None else [Board() for _ in range(9)]
        self._winner = None  # Cache winner calculation
    
    def get_board_winner(self, board_index: int) -> Optional[str]:
        """Get the winner of a specific board.
        
        Args:
            board_index: Index of the board to check (0-8).
            
        Returns:
            "X" or "O" if that player has won, "T" for a tie,
            or None if there is no winner yet.
        """
        if board_index < 0 or board_index > 8:
            return None
        return self.boards[board_index].get_winner()
    
    def get_winner(self) -> Optional[str]:
        """Check if there is a winner on the meta board.
        
        Returns:
            "X" or "O" if that player has won, "T" for a tie,
            or None if there is no winner yet.
        """
        # Use cached value if available
        if self._winner is not None:
            return self._winner
            
        # Create a meta-meta board based on winners of each board
        meta_squares = [self.get_board_winner(i) or "" for i in range(9)]
        meta_board = Board(meta_squares)
        
        # Get winner from meta board
        self._winner = meta_board.get_winner()
        return self._winner
    
    def is_valid_move(self, board_index: int, position: int, next_board: Optional[int]) -> bool:
        """Check if a move is valid given the current game state.
        
        Args:
            board_index: Index of the board to make a move on (0-8).
            position: Position on the board to make the move (0-8).
            next_board: The next board that play is restricted to, or None if any board is valid.
            
        Returns:
            True if the move is valid, False otherwise.
        """
        # Check if indices are valid
        if board_index < 0 or board_index > 8 or position < 0 or position > 8:
            return False
            
        # Check if the move is in the correct board
        if next_board is not None and board_index != next_board:
            return False
            
        # Check if the selected board has a winner
        if self.get_board_winner(board_index) is not None:
            return False
            
        # Check if the position is empty
        return self.boards[board_index].squares[position] == ""
    
    def make_move(self, board_index: int, position: int, player: str) -> bool:
        """Make a move on the meta board.
        
        Args:
            board_index: Index of the board to make a move on (0-8).
            position: Position on the board to make the move (0-8).
            player: The player making the move ("X" or "O").
            
        Returns:
            True if the move was valid and made, False otherwise.
        """
        # Check if indices are valid
        if board_index < 0 or board_index > 8 or position < 0 or position > 8:
            return False
            
        # Make the move on the appropriate board
        if self.boards[board_index].make_move(position, player):
            # Reset winner cache
            self._winner = None
            return True
        
        return False
    
    def get_next_board(self, last_position: int) -> Optional[int]:
        """Determine the next board to play on based on the last move.
        
        Args:
            last_position: The position of the last move (0-8).
            
        Returns:
            The index of the next board to play on, or None if the
            corresponding board is already won/tied and play can be
            on any board.
        """
        # Check if the specified board already has a winner
        if self.get_board_winner(last_position) is not None:
            return None
        
        return last_position