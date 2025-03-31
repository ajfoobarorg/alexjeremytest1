# Error Handling Specification

This specification defines the error handling requirements for the Ultimate Tic-Tac-Toe API.

## Overview

Proper error handling ensures that:

1. Clients receive clear, actionable error messages
2. The server maintains stability under error conditions
3. Debugging information is available when needed
4. Security is not compromised by exposing sensitive details

## Error Response Format

All error responses should follow a consistent format:

```json
{
  "detail": "Descriptive error message"
}
```

For multiple validation errors, the response may include more detailed information:

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "Username already exists",
      "type": "value_error"
    },
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

## HTTP Status Codes

The API should use appropriate HTTP status codes:

- **200 OK** - Successful request
- **400 Bad Request** - Invalid input, validation errors
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Authenticated but not authorized
- **404 Not Found** - Resource not found
- **409 Conflict** - Request conflicts with current state (e.g., duplicate username)
- **422 Unprocessable Entity** - Valid request but unable to process
- **500 Internal Server Error** - Server-side error

## Common Error Scenarios

### Authentication Errors

- Player not logged in (missing cookie)
- Invalid player ID
- Error message: "Not logged in" or "Invalid player ID"
- Status code: 401 Unauthorized

### Resource Not Found Errors

- Game not found
- Player not found
- Error message: "Game not found" or "Player not found"
- Status code: 404 Not Found

### Validation Errors

- Invalid email format
- Invalid timezone
- Invalid country code
- Username or email already exists
- Status code: 400 Bad Request

### Game Rule Violations

- Not player's turn
- Invalid move
- Move in wrong board
- Position already taken
- Board already completed
- Status code: 400 Bad Request

### Matchmaking Errors

- Player not in matchmaking
- Could not add player to matchmaking
- Status code: 400 Bad Request

### Time Control Errors

- Time control exceeded
- Error message: "Time control exceeded - game forfeited"
- Status code: 200 OK (this is a valid game state change, not an error)

## Error Logging

The API should log errors with appropriate severity levels:

- **DEBUG** - Detailed information for debugging
- **INFO** - Confirmation of expected events
- **WARNING** - Unexpected events that don't affect functionality
- **ERROR** - Runtime errors that affect functionality
- **CRITICAL** - Critical errors that require immediate attention

Log entries should include:

- Timestamp
- Severity level
- Error message
- Stack trace (for server errors)
- Request details (path, method, user)
- Correlation ID to track related events

## Security Considerations

1. Do not expose sensitive information in error messages
2. Avoid exposing implementation details or stack traces to clients
3. Use generic error messages for security-related failures
4. Log detailed error information server-side for debugging

## Custom Error Types

The API should define custom error types for common scenarios:

- `ValidationError` - Input validation errors
- `AuthenticationError` - Authentication failures
- `ResourceNotFoundError` - Resource not found
- `GameRuleViolationError` - Game rule violations
- `MatchmakingError` - Matchmaking issues

## Error Handling in Game Logic

Game logic should handle errors as follows:

1. Board position errors should throw exceptions with clear messages
2. Game move errors should return a tuple of (game, error_message)
3. Invalid game state changes should prevent the action and return appropriate errors

## Implementation Notes

1. Use a global error handler to ensure consistent formatting
2. Implement proper exception handling for all database operations
3. Include request IDs in responses for tracing errors
4. Configure appropriate logging levels based on environment (development, production)
5. Consider implementing rate limiting with appropriate error responses
6. Set up monitoring for error patterns to identify systemic issues