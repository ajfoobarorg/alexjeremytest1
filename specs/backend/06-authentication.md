# Authentication and User Management Specification

This specification defines the authentication and user management system for Ultimate Tic-Tac-Toe.

## Overview

The authentication system uses a simple cookie-based approach without password authentication. Users sign up or log in with their email, and receive an HttpOnly cookie that identifies them for subsequent requests.

## User Registration

### Process

1. User provides their username, email, and optional profile information
2. System validates the input:
   - Ensures username is unique
   - Ensures email is unique and valid
   - Validates timezone and country if provided
3. Creates a new Player record with a unique ID
4. Sets an HttpOnly cookie with the player ID
5. Returns the player ID to the client

### Initial ELO Rating

New players receive an initial ELO rating based on their self-reported level:
- Level 0 (New): 200
- Level 1 (Beginner): 400
- Level 2 (Intermediate): 700
- Level 3 (Advanced): 900

## Login

### Process

1. User provides their email
2. System looks up the player by email
3. If found, sets an HttpOnly cookie with the player ID
4. Returns the player ID to the client

### Error Handling

- If email is not found, returns a 404 Not Found error

## Logout

### Process

1. System deletes the player ID cookie
2. Returns a success message

## Cookie Security

Cookies should be configured with the following settings:

- HttpOnly: true (prevents JavaScript access to the cookie)
- SameSite: "none" in production, "lax" in development
- Secure: true in production, false in development
- Max Age: 1 year (365 days)
- Path: "/"
- Domain: Configured based on deployment environment

## User Profile Management

### Retrieving Profiles

Users can retrieve:
- Their own profile using the `/profile/me` endpoint (based on cookie)
- Any player's profile using the `/profile/{player_id}` endpoint

### Updating Profiles

Users can update their profile with the following constraints:
- Email uniqueness is maintained
- Username uniqueness is maintained
- Country code must be valid ISO 3166-1 alpha-2 
- Timezone must be a valid IANA timezone name

## Player Status and Statistics

### Player Stats

The system tracks the following stats per player:
- Wins
- Losses
- Draws
- ELO rating

### ELO Rating System

The ELO rating system works as follows:

1. After each game, both players' ratings are updated
2. The magnitude of change depends on:
   - The expected outcome (based on rating difference)
   - The actual outcome (win, loss, or draw)
3. Formula: `ELO_change = K * (actual_score - expected_score)`
   - K-factor: 32 (standard for most ELO systems)
   - Actual score: 1.0 for win, 0.5 for draw, 0.0 for loss
   - Expected score: 1 / (1 + 10^((opponent_elo - player_elo) / 400))

## Session Management

Sessions are entirely based on the presence of a valid cookie. There is no explicit session storage on the server side.

## Security Considerations

1. **No Password Authentication**: This system uses email-only authentication without passwords, which simplifies development but is not suitable for a production environment with sensitive data.

2. **CORS Configuration**: The backend should be configured with appropriate CORS settings to prevent unauthorized access from other domains.

3. **Cookie Security**: Cookies should be properly secured, especially in production environments.

4. **Input Validation**: All user inputs should be validated to prevent injection attacks and data corruption.