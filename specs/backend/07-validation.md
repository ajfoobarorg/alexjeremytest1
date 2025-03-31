# Input Validation Specification

This specification defines the validation requirements for the Ultimate Tic-Tac-Toe API.

## Overview

Input validation ensures that all data received by the API is correct, properly formatted, and safe to process. This includes validating request bodies, path parameters, query parameters, and cookies.

## Validation Framework

The API should use a schema validation framework that provides:

1. Type checking
2. Format validation
3. Constraint enforcement
4. Custom validation rules
5. Meaningful error messages

## Request Schemas

### SignupRequest

```
username: string - Required
email: string (email format) - Required
first_name: string? - Optional
last_name: string? - Optional
level: enum ("0", "1", "2", "3") - Required
timezone: string? - Optional, must be valid IANA timezone
country: string? - Optional, must be valid ISO 3166-1 alpha-2 code
```

### LoginRequest

```
email: string (email format) - Required
```

### ProfileUpdateRequest

```
username: string? - Optional
email: string? (email format) - Optional
first_name: string? - Optional
last_name: string? - Optional
location: string? - Optional
country: string? - Optional, must be valid ISO 3166-1 alpha-2 code
timezone: string? - Optional, must be valid IANA timezone
```

### MatchmakingRequest

```
player_id: string - Required
```

## Response Schemas

### GameResponse

```
id: string - Required
meta_board: string[9] - Required, array of 9 strings
boards: string[][9][9] - Required, 9 boards with 9 squares each
current_player: string - Required, must be "X" or "O"
next_board: integer? - Optional, must be 0-8 if present
winner: string? - Optional, must be "X" or "O" if present
started: boolean - Required
game_over: boolean - Required
player_x: {
  id: string? - Optional
  time_remaining: integer - Required, seconds
  elo_change: integer? - Optional
}
player_o: {
  id: string? - Optional
  time_remaining: integer - Required, seconds
  elo_change: integer? - Optional
}
```

### MatchmakingResponse

```
status: string - Required, one of "waiting", "waiting_acceptance", "matched", "cancelled", "error"
game_id: string? - Optional
opponent_name: string? - Optional
message: string? - Optional
```

### StatsResponse

```
games_today: integer - Required
players_online: integer - Required
```

## Path Parameter Validation

### Game ID

- Must be a valid UUID or other string ID format
- Must exist in the database (404 if not found)

### Board Index

- Must be an integer between 0 and 8
- Must be convertible to integer without loss

### Position

- Must be an integer between 0 and 8
- Must be convertible to integer without loss

### Player ID

- Must be a valid UUID or other string ID format
- Must exist in the database for most operations (404 if not found)

## Custom Validation Rules

### Timezone Validation

- Must be a string present in the IANA timezone database
- Examples: "America/New_York", "Europe/London", "Asia/Tokyo"

### Country Code Validation

- Must be a valid ISO 3166-1 alpha-2 code
- Examples: "US", "GB", "JP", "CA"
- Should normalize to uppercase

### Email Validation

- Must be a valid email format
- Uniqueness should be checked for signup and profile updates

### Username Validation

- Uniqueness should be checked for signup and profile updates

## Error Handling

When validation fails, the API should:

1. Return an appropriate HTTP status code (typically 400 Bad Request)
2. Include a descriptive error message in the response
3. Format the error response consistently

Example error response:

```json
{
  "detail": "Invalid timezone. Must be a valid IANA timezone name."
}
```

## Implementation Notes

1. Validation should occur as early as possible in the request pipeline
2. Re-use validation logic where possible to ensure consistency
3. Configure the validation framework to provide helpful error messages
4. Consider internationalization for error messages