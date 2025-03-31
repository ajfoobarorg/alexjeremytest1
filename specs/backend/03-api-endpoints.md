# API Endpoints Specification

This specification defines the API endpoints for the Ultimate Tic-Tac-Toe server.

## Authentication Endpoints

### POST /auth/signup

Register a new player.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "level": "string (0, 1, 2, or 3)", 
  "timezone": "string (optional)",
  "country": "string (optional)"
}
```

**Response:**
- Status: 200 OK
- Body: `{ "id": "string" }`
- Cookies: Sets `playerId` cookie

**Error Responses:**
- 400 Bad Request - Username already exists or email already exists

### POST /auth/login

Log in a player with email.

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
- Status: 200 OK
- Body: `{ "player_id": "string" }`
- Cookies: Sets `playerId` cookie

**Error Responses:**
- 404 Not Found - Email not found

### POST /auth/logout

Log out a player.

**Response:**
- Status: 200 OK
- Body: `{ "message": "Logged out successfully" }`
- Cookies: Clears `playerId` cookie

## Profile Endpoints

### GET /profile/me

Get the current player's profile based on cookie.

**Response:**
- Status: 200 OK
- Body:
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "location": "string (optional)",
  "country": "string (optional)",
  "timezone": "string (optional)",
  "stats": {
    "wins": "integer",
    "losses": "integer",
    "draws": "integer",
    "elo": "integer"
  }
}
```

**Error Responses:**
- 401 Unauthorized - Not logged in
- 404 Not Found - Player not found

### GET /profile/{player_id}

Get a player's profile by ID.

**Path Parameters:**
- `player_id`: String - ID of the player

**Response:**
- Status: 200 OK
- Body: Same as `/profile/me`

**Error Responses:**
- 404 Not Found - Player not found

### POST /profile/{player_id}

Update a player's profile.

**Path Parameters:**
- `player_id`: String - ID of the player

**Request Body:**
```json
{
  "username": "string (optional)",
  "email": "string (optional)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "location": "string (optional)",
  "country": "string (optional)",
  "timezone": "string (optional)"
}
```

**Response:**
- Status: 200 OK
- Body: Same as `/profile/me`

**Error Responses:**
- 400 Bad Request - Email already registered or username already taken
- 404 Not Found - Player not found

## Game Endpoints

### GET /games/{game_id}

Get details for a game.

**Path Parameters:**
- `game_id`: String - ID of the game

**Response:**
- Status: 200 OK
- Body:
```json
{
  "id": "string",
  "meta_board": ["string", ...], // 9 elements
  "boards": [["string", ...], ...], // 9 boards with 9 elements each
  "current_player": "string", // "X" or "O"
  "next_board": "integer (optional)", // 0-8 or null
  "winner": "string (optional)", // "X", "O", or null
  "started": "boolean",
  "game_over": "boolean",
  "player_x": {
    "id": "string (optional)",
    "time_remaining": "integer", // in seconds
    "elo_change": "integer (optional)"
  },
  "player_o": {
    "id": "string (optional)",
    "time_remaining": "integer", // in seconds
    "elo_change": "integer (optional)"
  }
}
```

**Error Responses:**
- 404 Not Found - Game not found

### POST /games/{game_id}/move/{board_index}/{position}

Make a move in a game.

**Path Parameters:**
- `game_id`: String - ID of the game
- `board_index`: Integer - Index of the board (0-8)
- `position`: Integer - Position on the board (0-8)

**Query Parameters:**
- `player_id`: String - ID of the player making the move

**Response:**
- Status: 200 OK
- Body: Same as `GET /games/{game_id}`

**Error Responses:**
- 400 Bad Request - Various errors (not your turn, invalid move, etc.)
- 404 Not Found - Game not found

### POST /games/{game_id}/resign

Resign from a game.

**Path Parameters:**
- `game_id`: String - ID of the game

**Query Parameters:**
- `player_id`: String - ID of the resigning player

**Response:**
- Status: 200 OK
- Body: Same as `GET /games/{game_id}`

**Error Responses:**
- 404 Not Found - Game not found

### POST /games/{game_id}/ready

Signal that player X is ready to start the game.

**Path Parameters:**
- `game_id`: String - ID of the game

**Query Parameters:**
- `player_id`: String - ID of the player (must be player X)

**Response:**
- Status: 200 OK
- Body: Same as `GET /games/{game_id}`

**Error Responses:**
- 400 Bad Request - Only player X can signal ready
- 404 Not Found - Game not found

## Matchmaking Endpoints

### POST /matchmaking/join

Join the matchmaking queue.

**Request Body:**
```json
{
  "player_id": "string"
}
```

**Response:**
- Status: 200 OK
- Body:
```json
{
  "status": "waiting"
}
```

**Error Responses:**
- 400 Bad Request - Could not add player to matchmaking

### POST /matchmaking/ping

Ping to check matchmaking status and keep player in queue.

**Request Body:**
```json
{
  "player_id": "string"
}
```

**Response:**
- Status: 200 OK
- Body (waiting):
```json
{
  "status": "waiting"
}
```
- Body (match found, waiting for acceptance):
```json
{
  "status": "waiting_acceptance",
  "opponent_name": "string"
}
```
- Body (match accepted, game created):
```json
{
  "status": "matched",
  "game_id": "string",
  "opponent_name": "string"
}
```

**Error Responses:**
- 400 Bad Request - Various errors

### POST /matchmaking/cancel

Cancel matchmaking for a player.

**Request Body:**
```json
{
  "player_id": "string"
}
```

**Response:**
- Status: 200 OK
- Body:
```json
{
  "status": "cancelled"
}
```

**Error Responses:**
- 400 Bad Request - Player not in matchmaking

## Stats Endpoint

### GET /stats

Get global game statistics.

**Response:**
- Status: 200 OK
- Body:
```json
{
  "games_today": "integer",
  "players_online": "integer"
}
```

## Health Endpoint

### GET /

Simple health check.

**Response:**
- Status: 200 OK
- Body:
```json
{
  "message": "Ultimate Tic-Tac-Toe API"
}
```