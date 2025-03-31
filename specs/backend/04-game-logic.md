# Game Logic Specification

This specification defines the game logic for Ultimate Tic-Tac-Toe.

## Board Class

The `Board` class represents a single 3×3 tic-tac-toe board.

### Properties

- `_squares`: A list of 9 strings, representing the state of each square ("X", "O", or "" for empty)

### Methods

#### `get(pos: int) -> str`

Gets the value at a specific position.

**Parameters:**
- `pos`: Integer between 0-8 representing the position on the board
  - 0 1 2
  - 3 4 5
  - 6 7 8

**Returns:**
- The value at the position ("X", "O", or "")

**Errors:**
- Raises an error if position is out of bounds

#### `set(pos: int, value: str) -> None`

Sets a value at a specific position.

**Parameters:**
- `pos`: Integer between 0-8 representing the position on the board
- `value`: String - must be "X", "O", or ""

**Returns:**
- None

**Errors:**
- Raises an error if position is out of bounds
- Raises an error if value is not valid

#### `to_list() -> List[str]`

Converts the board to a list representation.

**Returns:**
- A list of 9 strings representing the board state

#### `is_full() -> bool`

Checks if the board is full (no empty squares).

**Returns:**
- `true` if the board is full, `false` otherwise

#### `check_winner() -> Optional[str]`

Checks if there's a winner on the board.

**Returns:**
- "X" if X has won
- "O" if O has won
- `null` if no winner

#### `check_winner_from_list(board_as_list: List[str]) -> Optional[str]` (static)

Checks if there's a winner from a list representation of a board.

**Parameters:**
- `board_as_list`: A list of 9 strings representing a board

**Returns:**
- "X" if X has won
- "O" if O has won
- `null` if no winner

## MetaBoard Class

The `MetaBoard` class represents the meta-state of 9 boards (won/tied/available).

### Properties

- `_state`: A list of 9 strings ("X", "O", "T" for tie, or "" for still in play)

### Methods

#### `__init__(boards: List[Board])`

Initializes a meta-board from a list of Board objects.

**Parameters:**
- `boards`: A list of 9 Board objects

**Errors:**
- Raises an error if not exactly 9 boards are provided

#### `get_winner() -> Optional[str]`

Returns the winner of the meta-board.

**Returns:**
- "X" if X has won
- "O" if O has won
- `null` if no winner

#### `is_full() -> bool`

Checks if the meta-board is full (no empty spaces).

**Returns:**
- `true` if all boards are completed (won or tied), `false` otherwise

#### `is_board_playable(board_index: int) -> bool`

Checks if a specific board can be played in.

**Parameters:**
- `board_index`: Integer between 0-8 representing the board to check

**Returns:**
- `true` if the board is still in play, `false` if it has been won or tied

**Errors:**
- Raises an error if board_index is out of bounds

#### `to_list() -> List[str]`

Returns a list representation of the meta-board.

**Returns:**
- A list of 9 strings representing the meta-board state

#### `to_json() -> str`

Returns a JSON string representation for database storage.

**Returns:**
- A JSON string representing the meta-board state

## Game State Management

The game state is managed through the following operations:

### Creating a New Game

1. Initialize a new Game with player_x and player_o
2. Set current_player to "X"
3. Initialize boards to 9 empty boards
4. Initialize time tracking with last_move_time and 0 seconds used for both players

### Making a Move

1. Verify it's the player's turn
2. Update time used by the current player
3. Check if player has run out of time
4. Verify the move is in the correct board (next_board)
5. Verify the board is playable and the position is empty
6. Make the move by updating the appropriate board
7. Check for a winner at the meta-board level
8. Check for a draw (all boards completed)
9. Determine the next board based on the position played
10. Switch the current player
11. Save the updated game state

### Time Control

Time control works as follows:

1. Each player has 360 seconds (6 minutes) total
2. Time used is tracked per player
3. When a player makes a move, the elapsed time since the last move is added to their time used
4. If a player exceeds their time limit, they forfeit the game
5. Time remaining is calculated as `TOTAL_TIME_ALLOWED - time_used`

### Game Completion

A game is completed when:

1. A player wins by creating three-in-a-row at the meta-board level
2. The game ends in a draw when all boards are completed with no winner
3. A player resigns
4. A player exceeds their time limit

When a game completes:

1. Set game_over to true
2. Set winner if applicable
3. Update player stats (wins, losses, draws)
4. Calculate and apply ELO rating changes