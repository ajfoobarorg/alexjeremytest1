# Data Models Specification

This specification defines the core data structures for the Ultimate Tic-Tac-Toe API.

## Player Model

The `Player` model represents a user of the system.

### Fields

| Field       | Type      | Description                                          | Constraints                   |
|-------------|-----------|------------------------------------------------------|-------------------------------|
| id          | String    | Unique identifier for the player                     | Primary key, auto-generated    |
| username    | String    | Player's username                                    | Required, unique, max 50 chars |
| email       | String    | Player's email address                               | Required, unique, max 255 chars|
| first_name  | String    | Player's first name                                  | Optional, max 50 chars         |
| last_name   | String    | Player's last name                                   | Optional, max 50 chars         |
| wins        | Integer   | Number of games won                                  | Default: 0                     |
| losses      | Integer   | Number of games lost                                 | Default: 0                     |
| draws       | Integer   | Number of games drawn                                | Default: 0                     |
| elo         | Integer   | Player's ELO rating                                  | Default based on level         |
| location    | String    | Player's location                                    | Optional, max 100 chars        |
| country     | String    | Player's country code                                | Optional, ISO 3166-1 alpha-2   |
| timezone    | String    | Player's timezone                                    | Optional, IANA timezone name   |
| created_at  | DateTime  | When the player account was created                  | Auto-generated                 |
| last_active | DateTime  | When the player was last active                      | Auto-updated                   |

### Validation Rules

1. Email must be a valid email format
2. Country code must be a valid ISO 3166-1 alpha-2 code (e.g., "US", "GB")
3. Timezone must be a valid IANA timezone name (e.g., "America/New_York")
4. Username must be unique within the system
5. Email must be unique within the system

## Game Model

The `Game` model represents a single Ultimate Tic-Tac-Toe game.

### Fields

| Field               | Type      | Description                                    | Constraints                  |
|---------------------|-----------|------------------------------------------------|------------------------------|
| id                  | String    | Unique identifier for the game                 | Primary key, auto-generated  |
| current_player      | String    | Player whose turn it is ("X" or "O")           | Default: "X"                 |
| next_board          | Integer   | Index of the board where next move must be made| Optional (0-8)               |
| winner              | String    | Winner of the game ("X", "O", or null)         | Optional                     |
| started             | Boolean   | Whether the game has started                   | Default: false               |
| game_over           | Boolean   | Whether the game has ended                     | Default: false               |
| created_at          | DateTime  | When the game was created                      | Auto-generated               |
| completed_at        | DateTime  | When the game ended                            | Optional                     |
| player_x            | Reference | Reference to Player model                      | Foreign key                  |
| player_o            | Reference | Reference to Player model                      | Foreign key                  |
| last_move_time      | DateTime  | When the last move was made                    | Auto-updated                 |
| player_x_time_used  | Integer   | Time used by player X in seconds               | Default: 0                   |
| player_o_time_used  | Integer   | Time used by player O in seconds               | Default: 0                   |
| player_x_elo_change | Integer   | ELO change for player X after game completion  | Optional                     |
| player_o_elo_change | Integer   | ELO change for player O after game completion  | Optional                     |
| boards              | JSON      | JSON representation of all 9 boards            | Default: empty boards        |

### Constants

- `TOTAL_TIME_ALLOWED = 360` (6 minutes in seconds)

## Board Model

The `Board` class represents a single tic-tac-toe board.

### Fields

| Field     | Type       | Description                           |
|-----------|------------|---------------------------------------|
| _squares  | List[String] | Array of 9 strings, each representing a square on the board |

### Methods

| Method        | Parameters                | Return Type   | Description                                     |
|---------------|---------------------------|---------------|-------------------------------------------------|
| get           | pos: Integer              | String        | Get value at position (0-8)                     |
| set           | pos: Integer, value: String | None        | Set value at position (0-8)                     |
| to_list       | None                      | List[String]  | Convert to list representation                  |
| is_full       | None                      | Boolean       | Check if board is full                          |
| check_winner  | None                      | String?       | Check if there's a winner ("X", "O", or null)   |

## MetaBoard Model

The `MetaBoard` class represents the state of the 9 larger boards in Ultimate Tic-Tac-Toe.

### Fields

| Field    | Type       | Description                                             |
|----------|------------|---------------------------------------------------------|
| _state   | List[String] | Array of 9 strings representing board states ("X", "O", "T" for tie, or "") |

### Methods

| Method           | Parameters           | Return Type   | Description                                     |
|------------------|----------------------|---------------|-------------------------------------------------|
| get_winner       | None                 | String?       | Return "X", "O" if there's a winner, null otherwise |
| is_full          | None                 | Boolean       | Check if meta-board is full                     |
| is_board_playable| board_index: Integer | Boolean       | Check if a specific board can be played in      |
| to_list          | None                 | List[String]  | Return list representation for API responses    |
| to_json          | None                 | String        | Return JSON string for database storage         |

## Serialization Format

All data models should support conversion to and from JSON for API responses and database storage.